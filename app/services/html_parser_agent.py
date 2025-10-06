"""AI Agent for parsing HTML course content using LangChain."""
import os
import re
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class CourseClass(BaseModel):
    """Model for a single course class."""
    modulo: str = Field(description="The module name or section title")
    nome_aula: str = Field(description="The name/title of the class")
    duracao: str = Field(description="Duration in HH:MM:SS format")


class CourseContent(BaseModel):
    """Model for the complete course content."""
    classes: List[CourseClass] = Field(description="List of all classes in the course")


class HTMLCourseParser:
    """AI-powered parser for extracting course content from HTML."""
    
    def __init__(self):
        """Initialize the HTML parser with Gemini AI model."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Use REST transport to avoid gRPC issues in serverless environments
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",  # Using latest model
            temperature=0.0,  # Low temperature for consistency
            google_api_key=api_key,
            transport="rest"  # Force REST API instead of gRPC for Vercel compatibility
        )
        
        # Setup output parser
        self.parser = PydanticOutputParser(pydantic_object=CourseContent)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in analyzing HTML from online course platforms.
Your task is to extract structured information about INDIVIDUAL course classes from HTML code.

IMPORTANT NOTE: The actual content (module names, class titles, descriptions) may be in English, Portuguese, or Spanish. Extract them exactly as they appear in the HTML.

CRITICAL RULES - READ CAREFULLY:
1. Extract EACH CLASS INDIVIDUALLY with its OWN duration
2. DO NOT sum up durations from multiple classes
3. DO NOT use the total module duration - use INDIVIDUAL class durations
4. Each entry should represent ONE SINGLE CLASS, not a module or group

IMPORTANT INSTRUCTIONS:
1. Identify the HTML structure pattern that contains INDIVIDUAL classes
2. Look for elements such as:
   - Modules/Chapters: usually in tags like <div id="chapter-..."> or similar with titles
   - INDIVIDUAL Classes: may be in <div id="list-content-...">, <li>, or list elements
   - Class names: in tags like <h4>, <p>, <span class="title">, or similar
   - INDIVIDUAL Durations: in <p class="contentTime">, <span class="duration">, or text with MM:SS or HH:MM:SS format

3. COMMON PATTERNS TO LOOK FOR:
   
   A) **Full Cycle / React Apps:**
   - Modules: <div id="chapter-XXXX"> with <p class="MuiTypography-root">Module Name</p>
   - INDIVIDUAL Classes: <div id="list-content-XXXX"> with:
     * Name: <span class="MuiTypography-displayBlock">Class Name</span>
     * Duration: <p class="contentTime">MM:SS</p> or <p class="contentTime">HH:MM:SS</p>
   - Pattern: Look for "MuiTypography-displayBlock" followed by "contentTime"
   - IMPORTANT: Each <div id="list-content-XXXX"> is ONE class with ONE duration
   
   B) **Udemy:**
   - Modules: <div id="chapter-X"> for modules
   - INDIVIDUAL Classes: <div id="list-content-X"> with <p class="title"> and <p class="contentTime">
   
   C) **Hotmart:**
   - Structures with classes like "lesson-item", "module-title"
   - Durations in elements with "duration"
   
   D) **Eduzz:**
   - Elements with "aula", "modulo" in classes or IDs
   
   E) **Coursera/EdX:**
   - Lists <ul> with <li> containing classes
   
   F) **Custom platforms:**
   - Any repetitive pattern of title + duration

4. DURATION FORMAT - CRITICAL RULES:
   - Extract the duration that appears NEXT TO or INSIDE each individual class element
   - IMPORTANT: Most platforms show durations in MM:SS format (minutes:seconds)
   - If you find HH:MM:SS (3 parts, e.g., 1:15:30), keep as is (01:15:30)
   - If you find XX:YY (2 parts), determine format based on context:
     * If XX > 23, it's ALWAYS MM:SS (e.g., 45:32 = 45 minutes 32 seconds → 00:45:32)
     * If XX ≤ 23 and YY ≤ 59, assume MM:SS (e.g., 12:30 = 12 minutes 30 seconds → 00:12:30)
     * Exception: If the value is clearly hours (e.g., "2:00" for a 2-hour class), use HH:MM:SS (02:00:00)
   - Special cases:
     * 200:00 → This is 200 minutes (3h 20min), convert to 03:20:00
     * 120:00 → This is 120 minutes (2h), convert to 02:00:00
     * 02:00 → This is 2 minutes, convert to 00:02:00
   - If you find only MM (e.g., 15), convert to HH:MM:SS (00:15:00)
   - If no duration is found for a specific class, use "00:00:00"
   - NEVER use totals or sums - only individual class durations

5. MODULE EXTRACTION:
   - Look for elements that group classes (accordion, collapse, chapter, etc)
   - If no explicit modules are found, use "Module 1", "Module 2", etc
   - Each module should have a descriptive name
   - Use the module name as prefix for each class

6. EXAMPLES OF WHAT TO EXTRACT:
   CORRECT ✓:
   - Module: "Introduction", Class: "Welcome video", Duration: "00:05:30"
   - Module: "Introduction", Class: "Course overview", Duration: "00:10:15"
   
   WRONG ✗:
   - Module: "Introduction", Class: "All classes", Duration: "00:15:45" (this is a sum!)

7. CRITICAL VALIDATION:
   - Count the number of individual class elements in the HTML
   - Your output should have approximately the same number of classes
   - If you see 50 class elements, you should extract ~50 classes, not 5
   - DO NOT INVENT classes that don't exist in the HTML
   - DO NOT OMIT classes that are present
   - Extract ALL INDIVIDUAL classes found
   - Maintain the original order of classes

{format_instructions}

Analyze the provided HTML and extract all INDIVIDUAL classes with their INDIVIDUAL durations in the specified format."""),
            ("user", "Course HTML:\n\n{html_content}")
        ])
        
        self.chain = self.prompt | self.model | self.parser
    
    def parse_html_to_course_data(self, html_content: str) -> CourseContent:
        """Parse HTML and extract course structure using AI."""
        try:
            cleaned_html = self._clean_html(html_content)
            return self.chain.invoke({
                "html_content": cleaned_html,
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return CourseContent(classes=[])
    
    def _clean_html(self, html_content: str) -> str:
        """
        Advanced HTML cleaning to improve performance while preserving structure.
        
        This method removes non-essential content (scripts, styles, metadata) while
        keeping the structural elements needed for course content extraction.
        """
        # 1. Remove scripts (including inline scripts and external refs)
        html_content = re.sub(
            r'<script[^>]*>.*?</script>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # 2. Remove all style tags and their contents (CSS is not needed)
        html_content = re.sub(
            r'<style[^>]*>.*?</style>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # 3. Remove HTML comments
        html_content = re.sub(
            r'<!--.*?-->',
            '',
            html_content,
            flags=re.DOTALL
        )
        
        # 4. Remove inline style attributes (keeping class and id for structure)
        html_content = re.sub(
            r'\s+style\s*=\s*"[^"]*"',
            '',
            html_content,
            flags=re.IGNORECASE
        )
        
        # 5. Remove common metadata and non-content attributes
        # Remove data-* attributes (except data-duration which might contain time info)
        html_content = re.sub(
            r'\s+data-(?!duration)[a-zA-Z0-9\-]+\s*=\s*"[^"]*"',
            '',
            html_content
        )
        
        # 6. Remove SVG and image data URIs (they are huge and not needed)
        html_content = re.sub(
            r'<svg[^>]*>.*?</svg>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )
        html_content = re.sub(
            r'(src|href|background|background-image)\s*=\s*"data:image/[^"]*"',
            '',
            html_content,
            flags=re.IGNORECASE
        )
        
        # 7. Remove meta tags and link tags (not needed for content extraction)
        html_content = re.sub(
            r'<(meta|link)[^>]*>',
            '',
            html_content,
            flags=re.IGNORECASE
        )
        
        # 8. Remove empty or whitespace-only tags (except structural ones)
        # Do this BEFORE collapsing whitespace to avoid breaking content
        # Run multiple times to handle nested empty tags
        for _ in range(3):
            html_content = re.sub(
                r'<(span|div|i|b|strong|em)[^>]*>\s*</\1>',
                '',
                html_content,
                flags=re.IGNORECASE
            )
        
        # 9. Collapse multiple whitespaces WITHIN tags (preserving structure)
        # Replace multiple spaces/newlines/tabs with single space
        html_content = re.sub(r'[ \t]+', ' ', html_content)
        html_content = re.sub(r'\n+', '\n', html_content)
        
        # 10. Final size limit to avoid token limits
        # Keep first 150k chars (increased from 100k since we cleaned a lot)
        if len(html_content) > 150000:
            html_content = html_content[:150000]
        
        return html_content.strip()
    
    def _parse_duration_to_minutes(self, duration_str: str) -> float:
        """Convert duration string (HH:MM:SS, MM:SS, or MM) to minutes as float."""
        try:
            parts = list(map(int, duration_str.strip().split(':')))
            
            if len(parts) == 3:
                hours, minutes, seconds = parts
            elif len(parts) == 2:
                # Detect if it's HHH:MM (first > 59) or MM:SS
                if parts[0] > 59:
                    hours, minutes, seconds = parts[0], parts[1], 0
                else:
                    hours, minutes, seconds = 0, parts[0], parts[1]
            elif len(parts) == 1:
                hours, minutes, seconds = 0, parts[0], 0
            else:
                return 0.0
            
            # Convert to total minutes (including fractional seconds)
            total_minutes = hours * 60 + minutes + (seconds / 60.0)
            return total_minutes
            
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_html_to_classes_list(self, html_content: str) -> List[List]:
        """Parse HTML and return classes as [status, subject, duration_minutes]."""
        course_data = self.parse_html_to_course_data(html_content)
        
        classes = []
        for course_class in course_data.classes:
            duration_minutes = self._parse_duration_to_minutes(course_class.duracao)
            
            subject = f"{course_class.modulo}: {course_class.nome_aula}"
            classes.append(["Not Started", subject, duration_minutes])
        
        return classes


# Singleton instance
_parser_instance = None


def get_html_parser() -> HTMLCourseParser:
    """Get or create the HTML parser singleton instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = HTMLCourseParser()
    return _parser_instance
