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
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
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
    
    def check_for_more_like_this(self):
        """Check if we've reached the 'More Like This' section"""
        try:
            # Look for "More Like This" text or similar indicators
            more_like_this_indicators = [
                "More like this",
                "More ideas",
                "Related pins",
                "You might also like",
                "Similar ideas"
            ]
            
            page_text = self.driver.page_source.lower()
            for indicator in more_like_this_indicators:
                if indicator.lower() in page_text:
                    return True
            
            # Also check for specific elements that indicate recommendations
            try:
                recommendation_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'More like this') or contains(text(), 'More ideas') or contains(text(), 'Related')]")
                if recommendation_elements:
                    return True
            except:
                pass
                
            return False
        except:
            return False
    
    def scrape_board(self, board_url, max_pins=100, progress_callback=None):
        """Scrape Pinterest board for pin data - stops at 'More Like This' section"""
        try:
            if not self.driver:
                return self.get_demo_data(board_url, progress_callback)
            
            if progress_callback:
                progress_callback(f"🔍 Loading Pinterest board: {self.extract_board_name(board_url)}")
            
            self.driver.get(board_url)
            time.sleep(5)
            
            pins_data = []
            scroll_count = 0
            max_scrolls = 10
            consecutive_no_new_pins = 0
            reached_more_like_this = False
            
            while scroll_count < max_scrolls and consecutive_no_new_pins < 3 and not reached_more_like_this:
                # Check if we've reached "More Like This" section
                if self.check_for_more_like_this():
                    reached_more_like_this = True
                    if progress_callback:
                        progress_callback("🛑 Reached 'More Like This' section - stopping to avoid recommended pins")
                    break
                
                # Find pin elements
                pin_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-test-id="pin"]')
                
                # Filter out pins that are in recommendation sections
                valid_pins = []
                for pin in pin_elements:
                    try:
                        # Check if pin is in a recommendation section
                        parent_text = pin.find_element(By.XPATH, "./ancestor::*[contains(@class, 'recommend') or contains(@class, 'similar') or contains(@class, 'more')]").text.lower()
                        if any(word in parent_text for word in ['more like', 'similar', 'recommend', 'related']):
                            continue
                    except:
                        # If no recommendation parent found, it's likely a board pin
                        valid_pins.append(pin)
                
                initial_count = len(pins_data)
                
                if progress_callback:
                    if scroll_count == 0:
                        progress_callback(f"📌 Found {len(valid_pins)} pins initially. Scrolling to load more...")
                    else:
                        progress_callback(f"📌 Loaded {len(valid_pins)} pins after scroll {scroll_count}")
                
                # Extract image URLs from valid pins only
                for pin in valid_pins:
                    if len(pins_data) >= max_pins:
                        break
                        
                    try:
                        img_element = pin.find_element(By.TAG_NAME, "img")
                        img_url = img_element.get_attribute("src")
                        
                        # Skip placeholder images and duplicates
                        if (img_url and 
                            img_url not in [p.get('image_url') for p in pins_data] and
                            not any(skip in img_url.lower() for skip in ['placeholder', 'loading', 'spinner']) and
                            ('pinimg.com' in img_url or 'pinterest' in img_url)):
                            
                            pins_data.append({
                                'image_url': img_url,
                                'title': img_element.get_attribute("alt") or f"Pinterest Pin {len(pins_data) + 1}",
                                'pin_url': pin.get_attribute("href") or ""
                            })
                    except:
                        continue
                
                new_pins_found = len(pins_data) - initial_count
                
                # Check if we found new pins
                if new_pins_found == 0:
                    consecutive_no_new_pins += 1
                else:
                    consecutive_no_new_pins = 0
                
                # Scroll to load more pins (but stop if we hit recommendations)
                if len(pins_data) < max_pins and consecutive_no_new_pins < 3:
                    # Scroll down gradually
                    self.driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
                    time.sleep(2)
                    
                    # Check again for "More Like This" after scrolling
                    if self.check_for_more_like_this():
                        reached_more_like_this = True
                        if progress_callback:
                            progress_callback("🛑 Reached 'More Like This' section - stopping")
                        break
                    
                    scroll_count += 1
                else:
                    break
            
            if progress_callback:
                if reached_more_like_this:
                    progress_callback("✅ Stopped at end of board (before recommendations)")
                elif consecutive_no_new_pins >= 3:
                    progress_callback("✅ Reached end of board - no more pins found")
                else:
                    progress_callback(f"✅ Collected maximum pins ({max_pins})")
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
                if colors:
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
        
        if failed_count > 0:
            st.warning(f"⚠️ {failed_count} images failed to analyze, using fallback colors")
        
        st.success(f"✅ Successfully analyzed {analyzed_count} images ({analyzed_count - failed_count} real, {failed_count} fallback)")
        
        if not all_colors:
            all_colors = self.generate_fallback_colors()
        
        return self.aggregate_colors(all_colors)
    
    def extract_colors_from_url(self, image_url):
        """Extract colors from image URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(image_url, timeout=15, headers=headers, stream=True)
            if response.status_code != 200:
                return None
            
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None
                
            image_data = response.content
            if len(image_data) < 1000:
                return None
                
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            if image.width > 800 or image.height > 800:
                image.thumbnail((800, 800), Image.Resampling.LANCZOS)
            
            color_thief = ColorThief(io.BytesIO(image_data))
            dominant_colors = color_thief.get_palette(color_count=6, quality=1)
            
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
            min_colors = {}
            for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
                r_c, g_c, b_c = webcolors.hex_to_rgb(key)
                rd = (r_c - rgb_color[0]) ** 2
                gd = (g_c - rgb_color[1]) ** 2
                bd = (b_c - rgb_color[2]) ** 2
                min_colors[(rd + gd + bd)] = name
            
            closest_color = min_colors[min(min_colors.keys())]
            return closest_color.title()
    
    def generate_fallback_colors(self):
        """Generate fallback colors when image analysis fails"""
        fallback_colors = [
            {'hex': '#8B7E73', 'name': 'Gray', 'rgb': (139, 126, 115)},
            {'hex': '#DAD5D2', 'name': 'Lightgray', 'rgb': (218, 213, 210)},
            {'hex': '#634135', 'name': 'Darkolivegreen', 'rgb': (99, 65, 53)},
            {'hex': '#B3B1AE', 'name': 'Darkgray', 'rgb': (179, 177, 174)},
            {'hex': '#342B1D', 'name': 'Darkslategray', 'rgb': (52, 43, 29)},
            {'hex': '#746041', 'name': 'Darkolivegreen', 'rgb': (116, 96, 65)},
            {'hex': '#C49D88', 'name': 'Rosybrown', 'rgb': (196, 157, 136)},
            {'hex': '#52787B', 'name': 'Dimgray', 'rgb': (82, 120, 123)},
            {'hex': '#B7895A', 'name': 'Peru', 'rgb': (183, 137, 90)},
            {'hex': '#C05658', 'name': 'Indianred', 'rgb': (192, 86, 88)}
        ]
        
        return fallback_colors
    
    def aggregate_colors(self, all_colors):
        """Aggregate and analyze color data - FIXED VERSION"""
        if not all_colors:
            return {
                'dominant_colors': [],
                'total_colors_analyzed': 0,
                'unique_colors': 0
            }
        
        try:
            # Simple color counting without complex operations
            color_counts = {}
            total_colors = 0
            
            for color in all_colors:
                if isinstance(color, dict) and 'hex' in color and 'name' in color:
                    key = color['hex']
                    total_colors += 1
                    
                    if key in color_counts:
                        color_counts[key]['count'] += 1
                    else:
                        color_counts[key] = {
                            'hex': color['hex'],
                            'name': color['name'],
                            'count': 1
                        }
            
            if total_colors == 0:
                return {
                    'dominant_colors': [],
                    'total_colors_analyzed': 0,
                    'unique_colors': 0
                }
            
            # Calculate percentages and create final list
            dominant_colors = []
            for color_data in color_counts.values():
                percentage = (color_data['count'] / total_colors) * 100
                dominant_colors.append({
                    'hex': color_data['hex'],
                    'name': color_data['name'],
                    'percentage': round(percentage, 1),
                    'count': color_data['count']
                })
            
            # Sort by percentage (highest first)
            dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
            
            return {
                'dominant_colors': dominant_colors[:10],
                'total_colors_analyzed': total_colors,
                'unique_colors': len(color_counts)
            }
            
        except Exception as e:
            st.error(f"Error in color aggregation: {str(e)}")
            # Return safe fallback
            return {
                'dominant_colors': [
                    {'hex': '#8B7E73', 'name': 'Gray', 'percentage': 25.0, 'count': 1},
                    {'hex': '#DAD5D2', 'name': 'Lightgray', 'percentage': 20.0, 'count': 1},
                    {'hex': '#634135', 'name': 'Darkolivegreen', 'percentage': 15.0, 'count': 1}
                ],
                'total_colors_analyzed': 4,
                'unique_colors': 3
            }
    
    def __del__(self):
        """Clean up driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
