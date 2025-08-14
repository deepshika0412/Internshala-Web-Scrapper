from flask import Flask, render_template, request, Response, redirect, url_for, flash
from flask_mail import Mail, Message
from collections import Counter
from internshala_scraper import get_internships
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import re
import logging

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

app.config.update(
    MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'True') == 'True',
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
)

mail = Mail(app)

# Caching
CACHE_TTL = 1800  # 30 minutes
_cache = {'jobs': None, 'ts': 0}

# Mock data for testing when scraper returns no data
MOCK_JOBS = [
    {
        'title': 'Python Backend Developer Intern, Data Analyst',
        'company': 'TechCorp Solutions',
        'location': 'Remote, Mumbai',
        'link': 'https://internshala.com/internship/python-backend-developer-intern',
        'duration': '6 months',
        'stipend_range': '₹15,000 - ₹25,000 per month'
    },
    {
        'title': 'Django Web Development Intern',
        'company': 'StartupHub India',
        'location': 'Work From Home',
        'link': 'https://internshala.com/internship/django-web-development-intern',
        'duration': '3 months',
        'stipend_range': '₹8,000 - ₹12,000 per month'
    },
    {
        'title': 'Flask API Developer Intern',
        'company': 'InnovateTech',
        'location': 'Remote, Bangalore',
        'link': 'https://internshala.com/internship/flask-api-developer-intern',
        'duration': '4 months',
        'stipend_range': '₹10,000 - ₹18,000 per month'
    },
    {
        'title': 'Python Data Science Intern',
        'company': 'DataAnalytics Pro',
        'location': 'Hybrid, Delhi',
        'link': 'https://internshala.com/internship/python-data-science-intern',
        'duration': '6 months',
        'stipend_range': '₹20,000 - ₹30,000 per month'
    },
    {
        'title': 'Full Stack Python Developer',
        'company': 'WebSolutions Ltd',
        'location': 'Remote, Pune',
        'link': 'https://internshala.com/internship/full-stack-python-developer',
        'duration': '5 months',
        'stipend_range': '₹12,000 - ₹22,000 per month'
    },
    {
        'title': 'Python Automation Intern',
        'company': 'AutoTech Systems',
        'location': 'Work From Home',
        'link': 'https://internshala.com/internship/python-automation-intern',
        'duration': '3 months',
        'stipend_range': '₹6,000 - ₹10,000 per month'
    },
    {
        'title': 'Django Frontend Developer',
        'company': 'CreativeWeb Studio',
        'location': 'Remote, Chennai',
        'link': 'https://internshala.com/internship/django-frontend-developer',
        'duration': '4 months',
        'stipend_range': '₹9,000 - ₹15,000 per month'
    },
    {
        'title': 'Python Machine Learning Intern',
        'company': 'AI Innovations',
        'location': 'Hybrid, Hyderabad',
        'link': 'https://internshala.com/internship/python-machine-learning-intern',
        'duration': '6 months',
        'stipend_range': '₹25,000 - ₹35,000 per month'
    },
    {
        'title': 'Flask Microservices Developer',
        'company': 'CloudTech Solutions',
        'location': 'Remote, Kolkata',
        'link': 'https://internshala.com/internship/flask-microservices-developer',
        'duration': '5 months',
        'stipend_range': '₹15,000 - ₹25,000 per month'
    },
    {
        'title': 'Python Testing Intern',
        'company': 'QualityAssurance Pro',
        'location': 'Work From Home',
        'link': 'https://internshala.com/internship/python-testing-intern',
        'duration': '3 months',
        'stipend_range': '₹7,000 - ₹12,000 per month'
    },
    {
        'title': 'Django E-commerce Developer',
        'company': 'ShopTech Solutions',
        'location': 'Remote, Ahmedabad',
        'link': 'https://internshala.com/internship/django-ecommerce-developer',
        'duration': '4 months',
        'stipend_range': '₹11,000 - ₹19,000 per month'
    },
    {
        'title': 'Python DevOps Intern',
        'company': 'DevOps Masters',
        'location': 'Hybrid, Jaipur',
        'link': 'https://internshala.com/internship/python-devops-intern',
        'duration': '6 months',
        'stipend_range': '₹18,000 - ₹28,000 per month'
    }
]

def get_jobs_cached():
    """Get jobs from cache or refresh if expired."""
    now = time.time()
    if _cache['jobs'] is None or now - _cache['ts'] > CACHE_TTL:
        try:
            logger.info("🔄 Refreshing jobs cache with real-time data...")
            jobs = get_internships()
            
            # If no real jobs found, use mock data
            if not jobs:
                logger.info("⚠️ No real-time jobs found, using mock data")
                jobs = MOCK_JOBS.copy()
                for job in jobs:
                    job['source'] = 'Mock Data'
                    job['scraped_at'] = datetime.now().isoformat()
            else:
                logger.info(f"✅ Real-time data fetched: {len(jobs)} jobs from multiple sources")
            
            _cache.update({'jobs': jobs, 'ts': now})
            logger.info(f"Cache refreshed with {len(jobs)} jobs")
        except Exception as e:
            logger.exception("Failed to refresh jobs")
            # Use mock data if cache is empty
            if _cache['jobs'] is None:
                logger.info("Using mock data due to scraper failure")
                return MOCK_JOBS.copy()
    return _cache['jobs'] or MOCK_JOBS.copy()

# Stopwords to filter out
STOPWORDS = {'the','a','an','and','or','to','for','with','in','on','of','by','at','from','is','are','as','be','this','that','you','we','they','it','its','have','has','had','will','would','could','should','may','might','can','must','shall','do','does','did','not','no','yes','but','if','then','else','when','where','why','how','what','which','who','whom','whose','there','here','up','down','out','off','over','under','again','further','then','once','more','most','other','some','such','only','own','same','so','than','too','very','just','now','well','also','back','even','still','way','take','every','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now'}

def tokenize_title(title):
    """Extract meaningful words from job title."""
    words = re.findall(r'\b[a-zA-Z]+\b', title.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

# Generate trending chart
def generate_trending_chart(jobs):
    """Generate trending chart from job titles."""
    if not jobs:
        return
        
    tokens = [w for j in jobs for w in tokenize_title(j['title'])]
    if not tokens:
        return
        
    counter = Counter(tokens)
    common = counter.most_common(5)
    if not common:
        return
        
    labels, values = zip(*common)
    
    try:
        plt.figure(figsize=(8, 4))
        plt.bar(labels, values, color='skyblue')
        plt.title("Top 5 Trending Job Keywords")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Ensure static directory exists
        os.makedirs('static', exist_ok=True)
        plt.savefig("static/trending_fields.png", dpi=100, bbox_inches='tight')
        plt.close()
        logger.info("Trending chart generated successfully")
    except Exception as e:
        logger.exception("Failed to generate chart")

# Filter helpers
def extract_all_locations(jobs):
    locations = set()
    for job in jobs:
        for loc in job['location'].split(','):
            locations.add(loc.strip())
    return sorted(locations)

def extract_durations(jobs):
    return sorted(set(job['duration'] for job in jobs))

def extract_stipends(jobs):
    return sorted(set(job['stipend_range'] for job in jobs))

# Main route
@app.route('/', methods=['GET'])
def index():
    jobs = get_jobs_cached()
    
    # Generate chart only if cache was just refreshed
    if time.time() - _cache['ts'] < 60:  # Within 1 minute of refresh
        generate_trending_chart(jobs)

    query = request.args.get('search', '').lower()
    loc = request.args.get('location', '')
    duration = request.args.get('duration', '')
    stipend = request.args.get('stipend', '')

    # Filtering
    filtered = []
    for job in jobs:
        if query and query not in job['title'].lower():
            continue
        if loc and loc not in job['location']:
            continue
        if duration and duration != job['duration']:
            continue
        if stipend and stipend != job['stipend_range']:
            continue
        filtered.append(job)

    # Pagination
    page = int(request.args.get('page', 1))
    per_page = 10
    total = (len(filtered) + per_page - 1) // per_page
    paginated = filtered[(page - 1) * per_page: page * per_page]

    # Filters
    locations = extract_all_locations(jobs)
    durations = extract_durations(jobs)
    stipends = extract_stipends(jobs)

    # Trending tags
    tag_counter = Counter(w.lower() for j in jobs for w in j['title'].split())
    top_tags = [tag for tag, _ in tag_counter.most_common(5)]

    # Show message if using mock data
    if jobs == MOCK_JOBS:
        flash("ℹ️ Showing sample data for demonstration. Real-time data will appear when available.")

    return render_template('index.html',
                           jobs=paginated,
                           locations=locations,
                           durations=durations,
                           stipends=stipends,
                           search=query,
                           sel_loc=loc,
                           sel_dur=duration,
                           sel_stipend=stipend,
                           page=page,
                           total_pages=total,
                           trending_tags=top_tags)

# CSV Download
@app.route('/download')
def download_csv():
    jobs = get_jobs_cached()

    def gen():
        yield 'Title,Company,Location,Link\n'
        for j in jobs:
            title = j['title'].replace(',', ' ')
            company = j['company'].replace(',', ' ')
            location = j['location'].replace(',', ' ')
            link = j['link']
            yield f"{title},{company},{location},{link}\n"

    return Response(gen(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=internships.csv"})

# Email subscription
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '').strip()
    if not email:
        flash("❌ Email is required.")
        return redirect(url_for('index'))
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        flash("❌ Please enter a valid email address.")
        return redirect(url_for('index'))
    
    search = request.form.get('search', '')
    location = request.form.get('location', '')
    duration = request.form.get('duration', '')
    stipend = request.form.get('stipend', '')

    message_body = f"You're subscribed for alerts with:\nSearch: {search}\nLocation: {location}\nDuration: {duration}\nStipend: {stipend}"

    try:
        msg = Message("Internship Alert Subscription",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = message_body
        mail.send(msg)
        logger.info(f"Subscription email sent to {email}")
        flash("✅ Subscribed successfully! Check your email.")
    except Exception as e:
        logger.exception(f"Failed to send subscription email to {email}")
        flash("❌ Error sending email. Please try again later.")

    return redirect(url_for('index'))

@app.route('/refresh')
def refresh_data():
    """Manually refresh the job data."""
    try:
        # Clear cache to force refresh
        global _cache
        _cache = {'jobs': None, 'ts': 0}
        
        # Get fresh data
        jobs = get_jobs_cached()
        
        flash(f"✅ Data refreshed! Found {len(jobs)} jobs from multiple sources.")
        logger.info(f"Manual refresh completed with {len(jobs)} jobs")
        
    except Exception as e:
        flash(f"❌ Error refreshing data: {str(e)}")
        logger.exception("Manual refresh failed")
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
