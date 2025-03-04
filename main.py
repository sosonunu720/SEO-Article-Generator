
import os
import logging
import re
import markdown
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(prompt):
    try:
        # Use the gemini-1.5-flash model directly
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(prompt)
        return True, response.text
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return False, str(e)

def extract_titles(response_text):
    """Extract numbered titles from the response text."""
    # Look for numbered items (1. Title)
    titles = re.findall(r'^\d+\.\s+(.+)$', response_text, re.MULTILINE)
    
    # If that doesn't work, try looking for titles in quotes
    if not titles:
        titles = re.findall(r'"([^"]+)"', response_text)
    
    # If still no titles, just split by newlines and clean
    if not titles:
        titles = [line.strip() for line in response_text.split('\n') 
                 if line.strip() and not line.strip().startswith('```')]
    
    # Limit to 10 titles max
    return titles[:10]

def format_article_html(article_text):
    """Convert markdown to HTML and apply additional formatting."""
    # Convert markdown to HTML
    html = markdown.markdown(article_text)
    
    # Additional formatting if needed
    # Replace double newlines with paragraph breaks
    html = html.replace('\n\n', '</p><p>')
    
    return html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-titles', methods=['POST'])
def generate_titles():
    data = request.json
    main_keyword = data.get('mainKeyword', '').strip()
    seed_keywords = data.get('seedKeywords', '').strip()
    
    if not main_keyword:
        return jsonify({'success': False, 'message': 'Main keyword is required'})
    
    # Create prompt for title generation
    prompt = f"""Generate 10 unique and SEO-optimized article titles for the main keyword: "{main_keyword}".
    
    Additional seed keywords to incorporate (where appropriate): {seed_keywords}
    
    Requirements:
    - Each title should be compelling and click-worthy
    - Titles should be between 50-60 characters
    - Include numbers where appropriate (e.g., "7 Ways to...")
    - Use power words to increase engagement
    - Ensure each title is unique and different from others
    - Format as a numbered list from 1-10
    
    Please ONLY return the 10 titles as a numbered list, nothing else."""
    
    success, response = get_gemini_response(prompt)
    
    if success:
        titles = extract_titles(response)
        if titles and len(titles) > 0:
            return jsonify({
                'success': True,
                'titles': titles
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Could not extract titles from the response'
            })
    else:
        return jsonify({
            'success': False,
            'message': response
        })

@app.route('/generate-article', methods=['POST'])
def generate_article():
    data = request.json
    title = data.get('title', '').strip()
    main_keyword = data.get('mainKeyword', '').strip()
    seed_keywords = data.get('seedKeywords', '').strip()
    
    if not title or not main_keyword:
        return jsonify({'success': False, 'message': 'Title and main keyword are required'})
    
    # Create prompt for article generation
    prompt = f"""Write a comprehensive, SEO-optimized article with the title: "{title}"
    
    Main focus keyword: {main_keyword}
    Additional keywords to include (where natural): {seed_keywords}
    
    Requirements:
    1. Start with an engaging introduction that hooks the reader
    2. Create proper hierarchical structure with h2 and h3 headings
    3. Include bullet points or numbered lists where appropriate
    4. If relevant, include a comparison table
    5. Use data-driven points where possible
    6. Conclude with a clear summary and call to action
    7. Format the entire article in Markdown
    8. Article should be 800-1200 words
    9. Make sure the content is entirely unique and plagiarism-free
    10. Optimize naturally for SEO without keyword stuffing
    
    Format your response using proper Markdown:
    - Use # for the main title
    - Use ## for main headings (h2)
    - Use ### for subheadings (h3)
    - Use * or - for bullet points
    - Use 1. 2. 3. for numbered lists
    - Use | | | with header rows for tables
    
    Please ONLY return the article content in markdown format, nothing else."""
    
    success, response = get_gemini_response(prompt)
    
    if success:
        # Convert markdown article to HTML
        article_html = format_article_html(response)
        return jsonify({
            'success': True,
            'article': article_html,
            'raw_markdown': response
        })
    else:
        return jsonify({
            'success': False,
            'message': response
        })

@app.route('/model-info')
def model_info():
    try:
        available_models = []
        for model in genai.list_models():
            model_info = {
                'name': model.name,
                'display_name': model.display_name,
                'supported_methods': model.supported_generation_methods
            }
            available_models.append(model_info)
        
        return jsonify({
            'success': True,
            'models': available_models
        })
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
