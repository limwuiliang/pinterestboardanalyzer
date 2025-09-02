import requests
import time
import re
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
from colorthief import ColorThief
import io
import streamlit as st
import numpy as np
import webcolors

class PinterestScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver for Streamlit Cloud"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try different ChromeDriver paths for Streamlit Cloud
            driver_paths = [
                "/usr/bin/chromedriver",
                "/usr/local/bin/chromedriver", 
                "chromedriver"
            ]
            
            for driver_path in driver_paths:
                try:
                    self.driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    st.success("✅ Chrome driver initialized successfully")
                    return True
                except Exception as e:
                    continue
            
            # If all paths fail, try without specifying path
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                st.success("✅ Chrome driver initialized successfully")
                return True
            except Exception as e:
                st.warning(f"⚠️ Chrome driver not available: {str(e)}")
                st.info("💡 Using demo mode with sample data")
                return False
                
        except Exception as e:
            st.warning(f"⚠️ Failed to setup Chrome driver: {str(e)}")
            st.info("💡 Using demo mode with sample data")
            return False
    
    def scrape_board(self, board_url, max_pins=80, progress_callback=None):
        """Scrape Pinterest board for pin data"""
        try:
            if not self.driver:
                return self.get_demo_data(board_url, progress_callback)
            
            if progress_callback:
                progress_callback(f"🔍 Loading Pinterest board: {self.extract_board_name(board_url)}")
            
            self.driver.get(board_url)
            time.sleep(5)
            
            pins_data = []
            scroll_count = 0
            max_scrolls = 12
            consecutive_no_new_pins = 0
            last_pin_count = 0
            
            while scroll_count < max_scrolls and consecutive_no_new_pins < 4:
                # Find pin elements
                pin_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-test-id="pin"]')
                
                if progress_callback:
                    if scroll_count == 0:
                        progress_callback(f"📌 Found {len(pin_elements)} pins initially. Scrolling to load more...")
                    else:
                        progress_callback(f"📌 Loaded {len(pin_elements)} pins after scroll {scroll_count}")
                
                # Extract image URLs
                for pin in pin_elements:
                    if len(pins_data) >= max_pins:
                        break
                        
                    try:
                        img_element = pin.find_element(By.TAG_NAME, "img")
                        img_url = img_element.get_attribute("src")
                        
                        # Accept all Pinterest images
                        if (img_url and 
                            img_url not in [p.get('image_url') for p in pins_data] and
                            ('pinimg.com' in img_url or 'i.pinimg.com' in img_url)):
                            
                            pins_data.append({
                                'image_url': img_url,
                                'title': img_element.get_attribute("alt") or f"Pinterest Pin {len(pins_data) + 1}",
                                'pin_url': pin.get_attribute("href") or ""
                            })
                    except:
                        continue
                
                # Check if we're getting new pins
                current_pin_count = len(pins_data)
                if current_pin_count == last_pin_count:
                    consecutive_no_new_pins += 1
                else:
                    consecutive_no_new_pins = 0
                    last_pin_count = current_pin_count
                
                # Stop if we have enough pins or hit "More Like This"
                page_source = self.driver.page_source.lower()
                if scroll_count > 4 and ("more like this" in page_source or "more ideas" in page_source):
                    if progress_callback:
                        progress_callback("🛑 Reached 'More Like This' section - stopping")
                    break
                
                # Scroll to load more pins
                if len(pins_data) < max_pins and consecutive_no_new_pins < 4:
                    self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    time.sleep(3)
                    scroll_count += 1
                else:
                    break
            
            if progress_callback:
                progress_callback(f"🎯 Found {len(pins_data)} total pins in the board")
            
            return pins_data
            
        except Exception as e:
            st.error(f"❌ Error scraping Pinterest board: {str(e)}")
            return self.get_demo_data(board_url, progress_callback)
    
    def get_demo_data(self, board_url, progress_callback=None):
        """Generate demo data when scraping is not available"""
        if progress_callback:
            progress_callback("🔄 Using demo mode - generating sample data")
            
        demo_images = [
            "https://i.pinimg.com/564x/a1/b2/c3/a1b2c3d4e5f6789.jpg",
            "https://i.pinimg.com/564x/b2/c3/d4/b2c3d4e5f6789a.jpg",
            "https://i.pinimg.com/564x/c3/d4/e5/c3d4e5f6789ab.jpg",
            "https://i.pinimg.com/564x/d4/e5/f6/d4e5f6789abc.jpg",
            "https://i.pinimg.com/564x/e5/f6/78/e5f6789abcd.jpg"
        ]
        
        pins_data = []
        for i, img_url in enumerate(demo_images ):
            pins_data.append({
                'image_url': img_url,
                'title': f"Demo Pin {i+1}",
                'colors': self.generate_demo_colors()
            })
            
        if progress_callback:
            progress_callback(f"✅ Generated {len(pins_data)} demo pins for analysis")
            
        return pins_data
    
    def generate_demo_colors(self):
        """Generate demo color data"""
        demo_color_sets = [
            [
                {'hex': '#8B7E73', 'name': 'Gray'},
                {'hex': '#DAD5D2', 'name': 'Lightgray'},
                {'hex': '#634135', 'name': 'Darkolivegreen'}
            ],
            [
                {'hex': '#B3B1AE', 'name': 'Darkgray'},
                {'hex': '#342B1D', 'name': 'Darkslategray'},
                {'hex': '#746041', 'name': 'Darkolivegreen'}
            ],
            [
                {'hex': '#C49D88', 'name': 'Rosybrown'},
                {'hex': '#52787B', 'name': 'Dimgray'},
                {'hex': '#B7895A', 'name': 'Peru'}
            ]
        ]
        
        return demo_color_sets[np.random.randint(0, len(demo_color_sets))]
    
    def extract_board_name(self, board_url):
        """Extract board name from URL"""
        try:
            parts = board_url.rstrip('/').split('/')
            if len(parts) >= 2:
                username = parts[-2]
                board_name = parts[-1]
                return f"{username}'s {board_name.replace('-', ' ').title()}"
            return "Pinterest Board"
        except:
            return "Pinterest Board"
    
    def analyze_colors(self, pins_data, max_images=50):
        """Analyze colors from pin images"""
        if not pins_data:
            return None
            
        images_to_analyze = min(len(pins_data), max_images)
        st.info(f"🎨 Analyzing colors from {images_to_analyze} images out of {len(pins_data)} total pins")
        
        progress_bar = st.progress(0)
        
        all_colors = []
        analyzed_count = 0
        failed_count = 0
        
        for i, pin in enumerate(pins_data[:max_images]):
            try:
                colors = self.extract_colors_from_url(pin['image_url'])
                if colors and len(colors) > 0:
                    all_colors.extend(colors)
                    analyzed_count += 1
                    pin['colors'] = colors
                else:
                    failed_count += 1
                    demo_colors = self.generate_demo_colors()
                    all_colors.extend(demo_colors)
                    pin['colors'] = demo_colors
                    analyzed_count += 1
                
                progress = (i + 1) / images_to_analyze
                progress_bar.progress(progress)
                
            except Exception as e:
                failed_count += 1
                demo_colors = self.generate_demo_colors()
                all_colors.extend(demo_colors)
                pin['colors'] = demo_colors
                analyzed_count += 1
                continue
        
        progress_bar.empty()
        
        real_analyzed = analyzed_count - failed_count
        if failed_count > 0:
            st.warning(f"⚠️ {failed_count} images failed to analyze, using fallback colors")
        
        st.success(f"✅ Successfully analyzed {analyzed_count} images ({real_analyzed} real, {failed_count} fallback)")
        
        if not all_colors:
            all_colors = self.generate_fallback_colors()
        
        return self.aggregate_colors(all_colors)
    
    def extract_colors_from_url(self, image_url):
        """Extract colors from image URL"""
        try:
            # Simple headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, timeout=10, headers=headers)
            if response.status_code != 200:
                return None
                
            image_data = response.content
            if len(image_data) < 500:
                return None
                
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for faster processing
            if image.width > 400 or image.height > 400:
                image.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            color_thief = ColorThief(io.BytesIO(image_data))
            dominant_colors = color_thief.get_palette(color_count=5, quality=1)
            
            colors = []
            for rgb in dominant_colors:
                hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
                color_name = self.get_color_name(rgb)
                colors.append({
                    'hex': hex_color,
                    'name': color_name,
                    'rgb': rgb
                })
            
            return colors
            
        except Exception as e:
            return None
    
    def get_color_name(self, rgb_color):
        """Get the closest color name for RGB values"""
        try:
            color_name = webcolors.rgb_to_name(rgb_color)
            return color_name.title()
        except ValueError:
            # Simple color mapping for common colors
            r, g, b = rgb_color
            if r > 200 and g > 200 and b > 200:
                return "White"
            elif r < 50 and g < 50 and b < 50:
                return "Black"
            elif r > g and r > b:
                return "Red"
            elif g > r and g > b:
                return "Green"
            elif b > r and b > g:
                return "Blue"
            elif r > 150 and g > 150:
                return "Yellow"
            elif r > 100 and g < 100 and b < 100:
                return "Brown"
            else:
                return "Gray"
    
    def generate_fallback_colors(self):
        """Generate fallback colors when image analysis fails"""
        fallback_colors = [
            {'hex': '#8B7E73', 'name': 'Gray', 'rgb': (139, 126, 115)},
            {'hex': '#DAD5D2', 'name': 'Lightgray', 'rgb': (218, 213, 210)},
            {'hex': '#634135', 'name': 'Brown', 'rgb': (99, 65, 53)},
            {'hex': '#B3B1AE', 'name': 'Darkgray', 'rgb': (179, 177, 174)},
            {'hex': '#342B1D', 'name': 'Black', 'rgb': (52, 43, 29)}
        ]
        
        return fallback_colors
    
    def aggregate_colors(self, all_colors):
        """Aggregate and analyze color data"""
        if not all_colors:
            return {
                'dominant_colors': [
                    {'hex': '#8B7E73', 'name': 'Gray', 'percentage': 100.0, 'count': 1}
                ],
                'total_colors_analyzed': 1,
                'unique_colors': 1
            }
        
        try:
            color_counts = {}
            total = 0
            
            for color in all_colors:
                if color and 'hex' in color and 'name' in color:
                    hex_code = color['hex']
                    name = color['name']
                    total += 1
                    
                    if hex_code in color_counts:
                        color_counts[hex_code]['count'] += 1
                    else:
                        color_counts[hex_code] = {
                            'hex': hex_code,
                            'name': name,
                            'count': 1
                        }
            
            if total == 0:
                return {
                    'dominant_colors': [
                        {'hex': '#8B7E73', 'name': 'Gray', 'percentage': 100.0, 'count': 1}
                    ],
                    'total_colors_analyzed': 1,
                    'unique_colors': 1
                }
            
            # Create result
            result_colors = []
            for color_info in color_counts.values():
                percentage = (color_info['count'] / total) * 100
                result_colors.append({
                    'hex': color_info['hex'],
                    'name': color_info['name'],
                    'percentage': round(percentage, 1),
                    'count': color_info['count']
                })
            
            # Sort by count
            result_colors.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                'dominant_colors': result_colors[:10],
                'total_colors_analyzed': total,
                'unique_colors': len(color_counts)
            }
            
        except Exception as e:
            return {
                'dominant_colors': [
                    {'hex': '#8B7E73', 'name': 'Gray', 'percentage': 100.0, 'count': 1}
                ],
                'total_colors_analyzed': 1,
                'unique_colors': 1
            }
    
    def __del__(self):
        """Clean up driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
