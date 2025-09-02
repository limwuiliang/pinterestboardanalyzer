import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import io
from pinterest_scraper import PinterestScraper

# Page configuration
st.set_page_config(
    page_title="Pinterest Board Analyzer",
    page_icon="📌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def normalize_pinterest_url(url):
    """Normalize Pinterest URL to handle different formats"""
    if not url:
        return ""
    
    url = url.strip()
    
    # Add https:// if missing
    if not url.startswith(('http://', 'https://' )):
        url = 'https://' + url
    
    # Ensure it's a Pinterest URL
    if 'pinterest.com' not in url:
        return ""
    
    # Normalize www
    url = url.replace('www.pinterest.com', 'pinterest.com' )
    url = url.replace('pinterest.com', 'www.pinterest.com')
    
    # Ensure trailing slash
    if not url.endswith('/'):
        url += '/'
    
    return url

def create_color_palette_chart(color_data):
    """Create color palette visualization"""
    if not color_data or 'dominant_colors' not in color_data:
        return None
    
    colors = color_data['dominant_colors'][:10]
    
    if not colors:
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        num_colors = len(colors)
        cols = 5
        rows = (num_colors + cols - 1) // cols
        
        for i, color in enumerate(colors):
            row = i // cols
            col = i % cols
            
            rect = plt.Rectangle((col, rows - row - 1), 0.8, 0.8, 
                               facecolor=color['hex'], 
                               edgecolor='white', 
                               linewidth=2)
            ax.add_patch(rect)
            
            # Determine text color based on background
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            brightness = sum(rgb) / 3
            text_color = 'white' if brightness < 128 else 'black'
            
            ax.text(col + 0.4, rows - row - 0.3, 
                   f"{color['name']}\n{color['hex']}\n{color['percentage']:.1f}%",
                   ha='center', va='center', 
                   fontsize=10, fontweight='bold',
                   color=text_color)
        
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"🎨 Color Palette (from {st.session_state.get('total_pins', 0)} pins)", 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating color palette: {str(e)}")
        return None

def create_color_distribution_chart(color_data):
    """Create color distribution bar chart"""
    if not color_data or 'dominant_colors' not in color_data:
        return None
    
    colors = color_data['dominant_colors'][:10]
    
    if not colors:
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        color_names = [f"{c['name']}\n({c['hex']})" for c in colors]
        percentages = [c['percentage'] for c in colors]
        hex_colors = [c['hex'] for c in colors]
        
        bars = ax.bar(color_names, percentages, color=hex_colors, 
                     edgecolor='white', linewidth=2, alpha=0.9)
        
        for bar, percentage in zip(bars, percentages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{percentage:.1f}%', ha='center', va='bottom', 
                   fontweight='bold', fontsize=10)
        
        ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title('🎨 Color Distribution Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, max(percentages) * 1.2 if percentages else 1)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating distribution chart: {str(e)}")
        return None

def analyze_pinterest_board(board_url):
    """Analyze Pinterest board and return results"""
    try:
        # Clear previous results
        if 'analysis_results' in st.session_state:
            del st.session_state['analysis_results']
        
        scraper = PinterestScraper()
        
        # Progress tracking
        progress_placeholder = st.empty()
        
        def progress_callback(message):
            progress_placeholder.info(message)
        
        # Scrape board
        pins_data = scraper.scrape_board(board_url, progress_callback=progress_callback)
        
        if not pins_data:
            st.error("❌ Failed to analyze Pinterest board. Please check the URL and try again.")
            return None
        
        # Store total pins count
        st.session_state['total_pins'] = len(pins_data)
        
        # Analyze colors
        color_analysis = scraper.analyze_colors(pins_data)
        
        progress_placeholder.empty()
        
        return {
            'pins_data': pins_data,
            'color_analysis': color_analysis,
            'total_pins': len(pins_data)
        }
        
    except Exception as e:
        st.error(f"❌ Error analyzing Pinterest board: {str(e)}")
        return None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📌 Pinterest Board Analyzer</h1>
        <p>AI-powered color analysis and insights from Pinterest boards</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Analysis Options")
        
        # URL input
        st.markdown("📌 **Pinterest Board URL**")
        board_url = st.text_input(
            "Enter Pinterest board URL:",
            placeholder="https://www.pinterest.com/username/board-name/",
            help="Enter the full URL of a public Pinterest board"
         )
        
        # Analyze button
        if st.button("🔍 Analyze Board", type="primary"):
            if board_url:
                normalized_url = normalize_pinterest_url(board_url)
                if normalized_url:
                    with st.spinner("🔍 Analyzing Pinterest board..."):
                        results = analyze_pinterest_board(normalized_url)
                        if results:
                            st.session_state['analysis_results'] = results
                            st.success("✅ Analysis complete!")
                        else:
                            st.error("❌ Failed to analyze Pinterest board. Please check the URL and try again.")
                else:
                    st.error("❌ Please enter a valid Pinterest board URL")
            else:
                st.error("❌ Please enter a Pinterest board URL")
        
        # Clear cache button
        if st.button("🗑️ Clear Cache"):
            if 'analysis_results' in st.session_state:
                del st.session_state['analysis_results']
            if 'total_pins' in st.session_state:
                del st.session_state['total_pins']
            st.success("✅ Cache cleared!")
    
    # Main content
    if 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        
        # Analysis Summary
        st.subheader("📊 Analysis Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Pins Found",
                results['total_pins']
            )
        
        with col2:
            pins_analyzed = len([p for p in results['pins_data'] if 'colors' in p])
            st.metric(
                "Pins Analyzed", 
                pins_analyzed
            )
        
        with col3:
            coverage = (pins_analyzed / results['total_pins'] * 100) if results['total_pins'] > 0 else 0
            st.metric(
                "Coverage",
                f"{coverage:.1f}%"
            )
        
        with col4:
            unique_colors = results['color_analysis'].get('unique_colors', 0) if results['color_analysis'] else 0
            st.metric(
                "Unique Colors",
                unique_colors
            )
        
        # Color Analysis
        if results['color_analysis'] and 'dominant_colors' in results['color_analysis']:
            st.subheader("📊 Comprehensive Analysis Results")
            
            color_analysis = results['color_analysis']
            
            # Color palette chart
            st.subheader("🎨 Color Palette")
            palette_chart = create_color_palette_chart(color_analysis)
            if palette_chart:
                st.pyplot(palette_chart)
                plt.close(palette_chart)
            
            # Color distribution chart
            st.subheader("📊 Color Distribution")
            dist_chart = create_color_distribution_chart(color_analysis)
            if dist_chart:
                st.pyplot(dist_chart)
                plt.close(dist_chart)
            
            # Color details table
            st.subheader("📋 Detailed Color Breakdown")
            if color_analysis['dominant_colors']:
                color_df = pd.DataFrame(color_analysis['dominant_colors'])
                color_df = color_df[['name', 'hex', 'percentage', 'count']]
                color_df.columns = ['Color Name', 'Hex Code', 'Percentage (%)', 'Count']
                color_df['Percentage (%)'] = color_df['Percentage (%)'].round(1)
                st.dataframe(color_df, use_container_width=True)
            
            # Download options
            st.subheader("💾 Download Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # CSV download
                csv_data = pd.DataFrame(color_analysis['dominant_colors']).to_csv(index=False)
                st.download_button(
                    "📄 Download CSV",
                    csv_data,
                    "pinterest_colors.csv",
                    "text/csv"
                )
            
            with col2:
                # JSON download
                json_data = json.dumps(color_analysis, indent=2)
                st.download_button(
                    "📋 Download JSON",
                    json_data,
                    "pinterest_analysis.json",
                    "application/json"
                )
            
            with col3:
                # Adobe palette
                adobe_colors = []
                for color in color_analysis['dominant_colors'][:5]:
                    hex_color = color['hex'].lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    adobe_colors.append(f"{color['name']}: RGB({rgb[0]}, {rgb[1]}, {rgb[2]})")
                
                adobe_data = "\n".join(adobe_colors)
                st.download_button(
                    "🎨 Adobe Palette",
                    adobe_data,
                    "pinterest_palette.txt",
                    "text/plain"
                )
    
    else:
        # Welcome message
        st.info("👆 Enter a Pinterest board URL in the sidebar to start analyzing!")
        
        # Example URLs
        st.subheader("📌 Example Pinterest Boards")
        st.markdown("""
        Try these example boards:
        - `https://www.pinterest.com/pinterest/summer-cycling-apparel/`
        - `https://www.pinterest.com/pinterest/home-decor-ideas/`
        - `https://www.pinterest.com/pinterest/wedding-inspiration/`
        """ )

if __name__ == "__main__":
    main()
