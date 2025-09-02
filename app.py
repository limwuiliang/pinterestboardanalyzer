def create_color_palette_chart(color_data):
    """Create color palette visualization"""
    if not color_data or 'dominant_colors' not in color_data:
        return None
    
    colors = color_data['dominant_colors'][:10]  # Top 10 colors
    
    if not colors:
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create color swatches
        num_colors = len(colors)
        cols = 5
        rows = (num_colors + cols - 1) // cols
        
        for i, color in enumerate(colors):
            row = i // cols
            col = i % cols
            
            # Create rectangle for color swatch
            rect = plt.Rectangle((col, rows - row - 1), 0.8, 0.8, 
                               facecolor=color['hex'], 
                               edgecolor='white', 
                               linewidth=2)
            ax.add_patch(rect)
            
            # Add color name and percentage
            ax.text(col + 0.4, rows - row - 0.3, 
                   f"{color['name']}\n{color['hex']}\n{color['percentage']:.1f}%",
                   ha='center', va='center', 
                   fontsize=10, fontweight='bold',
                   color='white' if sum(int(color['hex'][i:i+2], 16) for i in (1, 3, 5)) < 400 else 'black')
        
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"🎨 Color Palette (from ALL {st.session_state.get('total_pins', 0)} pins)", 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating color palette: {str(e)}")
        return None

def create_color_wheel_chart(color_data):
    """Create color wheel visualization"""
    if not color_data or 'dominant_colors' not in color_data:
        return None
    
    colors = color_data['dominant_colors'][:8]  # Top 8 colors for wheel
    
    if not colors:
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Calculate angles for each color
        angles = np.linspace(0, 2 * np.pi, len(colors), endpoint=False)
        
        # Create color wheel
        for i, (angle, color) in enumerate(zip(angles, colors)):
            # Create wedge for each color
            wedge_width = 2 * np.pi / len(colors)
            ax.bar(angle, 1, width=wedge_width, 
                  color=color['hex'], alpha=0.8, 
                  edgecolor='white', linewidth=2)
            
            # Add labels
            label_angle = angle + wedge_width / 2
            ax.text(label_angle, 1.2, 
                   f"{color['name']}\n{color['percentage']:.1f}%",
                   ha='center', va='center',
                   fontsize=10, fontweight='bold',
                   rotation=np.degrees(label_angle) - 90 if np.cos(label_angle) < 0 else np.degrees(label_angle) + 90)
        
        ax.set_ylim(0, 1.5)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rticks([])
        ax.set_thetagrids([])
        ax.set_title("🎨 Color Wheel Distribution", fontsize=16, fontweight='bold', pad=30)
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating color wheel: {str(e)}")
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
        
        # Add percentage labels on bars
        for bar, percentage in zip(bars, percentages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{percentage:.1f}%', ha='center', va='bottom', 
                   fontweight='bold', fontsize=10)
        
        ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title('🎨 Color Distribution Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, max(percentages) * 1.2)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating distribution chart: {str(e)}")
        return None
