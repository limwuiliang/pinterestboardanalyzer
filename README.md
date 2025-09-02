# 🎨 Pinterest Board Analyzer

A comprehensive Pinterest board analysis tool that extracts real color data from Pinterest boards and generates professional visualizations using Python.

## ✨ Features

- **🔍 Real Pinterest Scraping**: Analyzes actual Pinterest boards with accurate pin counts
- **🎨 AI Color Analysis**: Extracts dominant colors from images using ColorThief and machine learning
- **📊 Python-Generated Charts**: Creates professional visualizations with matplotlib and plotly
- **📥 Export Options**: Download analysis as CSV, JSON, and Adobe palette files
- **🌍 Cultural Insights**: Provides trend predictions and cultural analysis
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🚀 Live Demo

Try the live application: [Pinterest Board Analyzer](https://your-app-name.streamlit.app)

## 📋 How to Use

1. **Enter Pinterest Board URL**: Paste any public Pinterest board URL
2. **Click Analyze**: The app will scrape the board and analyze images
3. **View Results**: See comprehensive color analysis, charts, and insights
4. **Download Data**: Export results in multiple formats

### Example URLs to Try:
- `https://pinterest.com/pinterest/summer-cycling-apparel/`
- `https://pinterest.com/pinterest/home-decor-ideas/`
- Any public Pinterest board URL

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit for interactive web interface
- **Backend**: Python with Selenium for web scraping
- **Color Analysis**: ColorThief + K-means clustering for dominant color extraction
- **Visualizations**: matplotlib, plotly, and seaborn for professional charts
- **Data Processing**: pandas and numpy for data manipulation

### Key Components
- `app.py`: Main Streamlit application
- `pinterest_scraper.py`: Pinterest board scraping and color analysis
- `requirements.txt`: Python dependencies

### Color Analysis Process
1. **Scraping**: Uses Selenium to extract image URLs from Pinterest boards
2. **Image Processing**: Downloads and processes images using PIL
3. **Color Extraction**: Uses ColorThief to identify dominant colors
4. **Color Naming**: Maps RGB values to human-readable color names
5. **Analysis**: Aggregates data and calculates percentages and trends

## 🚀 Deployment Instructions

### Deploy to Streamlit Cloud (Recommended)

1. **Fork this repository** to your GitHub account

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Sign in with GitHub**

4. **Click "New app"**

5. **Configure deployment**:
   - Repository: `your-username/pinterest-board-analyzer`
   - Branch: `main`
   - Main file path: `app.py`

6. **Click "Deploy"**

7. **Wait for deployment** (usually 2-5 minutes)

Your app will be available at: `https://your-app-name.streamlit.app`

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/pinterest-board-analyzer.git
cd pinterest-board-analyzer

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 🔧 Configuration

### Streamlit Cloud Setup

The app is optimized for Streamlit Cloud deployment with:
- Automatic ChromeDriver detection
- Fallback demo mode when browser automation isn't available
- Cloud-optimized Selenium configuration
- Responsive design for various screen sizes

### Browser Requirements

For full functionality, the app requires:
- Chrome/Chromium browser (automatically handled in Streamlit Cloud)
- Internet connection for Pinterest access
- JavaScript enabled

## 📊 Sample Analysis Output

The app provides comprehensive analysis including:

### Color Analysis
- **Dominant Colors**: Top 10 colors with percentages and hex codes
- **Color Temperature**: Warm vs. cool color distribution
- **Color Palette**: Visual swatches with names and percentages

### Visualizations
- **Color Distribution Chart**: Horizontal bar chart showing color percentages
- **Color Temperature Analysis**: Stacked bar chart of warm/cool/neutral colors
- **Interactive Color Wheel**: Plotly-based interactive visualization
- **Trend Confidence Chart**: Prediction confidence levels

### Cultural Insights
- **Cultural Movements**: Identified design trends
- **Zeitgeist Score**: Cultural relevance percentage
- **Generational Appeal**: Appeal across different age groups
- **Regional Preferences**: Geographic preference analysis

### Export Options
- **CSV**: Color data with percentages and hex codes
- **JSON**: Complete analysis results
- **Adobe Palette**: Color swatches for design software

## 🎯 Use Cases

- **Designers**: Extract color palettes for design projects
- **Marketers**: Analyze trending colors in specific niches
- **Researchers**: Study color preferences and cultural trends
- **Brands**: Understand color trends in their industry
- **Content Creators**: Identify popular aesthetic trends

## 🔍 Technical Limitations

- **Public Boards Only**: Can only analyze publicly accessible Pinterest boards
- **Rate Limiting**: Pinterest may limit scraping frequency
- **Image Quality**: Analysis quality depends on source image resolution
- **Browser Dependency**: Full functionality requires browser automation support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web app framework
- **ColorThief**: For color extraction capabilities
- **Selenium**: For web scraping functionality
- **Pinterest**: For providing the data source

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/your-username/pinterest-board-analyzer/issues) page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🔄 Updates

- **v2.0**: Real Pinterest scraping with accurate pin counts
- **v1.5**: Added cultural insights and trend predictions
- **v1.0**: Initial release with basic color analysis

---

**Made with ❤️ using Streamlit and Python**

