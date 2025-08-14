# Internship Finder

A Flask web application that scrapes and displays Python development internships from Internshala, with filtering, trending analysis, and email subscription features.

## Features

- 🔍 **Real-time Scraping**: Fetches latest Python development internships from Internshala
- 📊 **Trending Analysis**: Visualizes popular job keywords and skills
- 🔧 **Advanced Filtering**: Filter by location, duration, stipend, and search terms
- 📧 **Email Subscriptions**: Get notified about new internships matching your criteria
- 📥 **CSV Export**: Download internship data for offline analysis
- ⚡ **Smart Caching**: Reduces server load with 30-minute caching
- 🛡️ **Robust Error Handling**: Graceful handling of network issues and parsing errors

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd internship-finder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your_secure_secret_key_here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

   **Note**: For Gmail, you'll need to:
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the App Password in `MAIL_PASSWORD`

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   
   Open your browser and go to `http://localhost:5000`

## Usage

### Browsing Internships
- View all available Python development internships
- Use the search bar to find specific roles or skills
- Filter by location, duration, or stipend range
- Navigate through pages to see more results

### Trending Analysis
- View the trending chart showing popular job keywords
- This helps identify in-demand skills and technologies

### Email Subscriptions
- Enter your email address
- Optionally specify search criteria (location, duration, stipend)
- Receive email notifications about new matching internships

### Data Export
- Click "Download CSV" to export all internship data
- Use the CSV file for offline analysis or integration with other tools

## Technical Details

### Architecture
- **Backend**: Flask web framework
- **Scraping**: BeautifulSoup4 with requests
- **Caching**: In-memory cache with 30-minute TTL
- **Email**: Flask-Mail with SMTP
- **Charts**: Matplotlib for data visualization

### Security Features
- Environment variable configuration for sensitive data
- Proper error handling and logging
- Input validation for email subscriptions
- Respectful web scraping with headers and timeouts

### Performance Optimizations
- Smart caching reduces external API calls
- Efficient filtering and pagination
- Optimized chart generation (only when cache refreshes)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Randomly generated |
| `MAIL_SERVER` | SMTP server for email | smtp.gmail.com |
| `MAIL_PORT` | SMTP port | 587 |
| `MAIL_USE_TLS` | Use TLS encryption | True |
| `MAIL_USERNAME` | Email username | Required |
| `MAIL_PASSWORD` | Email password/app password | Required |

### Cache Settings

The application uses in-memory caching with the following settings:
- **Cache TTL**: 30 minutes (1800 seconds)
- **Refresh Strategy**: Only when cache expires or is empty
- **Fallback**: Returns empty list if scraping fails

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check your Gmail App Password
   - Ensure 2FA is enabled on your Gmail account
   - Verify SMTP settings in `.env`

2. **No internships showing**
   - Check internet connection
   - Internshala might be temporarily unavailable
   - Check application logs for errors

3. **Chart not generating**
   - Ensure `static/` directory exists
   - Check matplotlib installation
   - Verify write permissions

### Logs

The application logs important events to help with debugging:
- Cache refresh events
- Email sending attempts
- Chart generation status
- Scraping errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application scrapes data from Internshala for educational purposes. Please respect their terms of service and robots.txt file. The application includes appropriate delays and headers to be respectful to their servers. 