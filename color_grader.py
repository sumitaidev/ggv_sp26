import cv2
import numpy as np
from PIL import Image
import streamlit as st


def apply_color_grading(img, brightness, contrast, saturation, warm_cool, tint_color):
    """Applies standard color grading operations to an image."""
    # Convert PIL Image to numpy array (RGB)
    img_array = np.array(img)

    # 1. Adjust Brightness & Contrast
    # Formula: output = input * contrast + brightness
    contrast_factor = contrast / 100.0
    graded_img = cv2.convertScaleAbs(img_array, alpha=contrast_factor, beta=brightness)

    # 2. Adjust Saturation (Using HSV Color Space)
    hsv_img = cv2.cvtColor(graded_img, cv2.COLOR_RGB2HSV).astype("float32")
    hsv_img[:, :, 1] = hsv_img[:, :, 1] * (saturation / 100.0)
    # Clip values to stay within valid 0-255 range
    hsv_img[:, :, 1] = np.clip(hsv_img[:, :, 1], 0, 255)
    graded_img = cv2.cvtColor(hsv_img.astype("uint8"), cv2.COLOR_HSV2RGB)

    # 3. Adjust Temperature / Warm-Cool Balance
    # Warm increases Red/Yellow; Cool increases Blue
    r, g, b = cv2.split(graded_img)
    if warm_cool > 0:  # Warmer
        r = cv2.add(r, warm_cool)
        g = cv2.add(g, warm_cool // 2)
    elif warm_cool < 0:  # Cooler
        b = cv2.add(b, abs(warm_cool))
        g = cv2.add(g, abs(warm_cool) // 4)

    # 4. Apply a Stylized Color Tint Filter (Creative Grading)
    if tint_color == "Cinematic Teal & Orange":
        # Boost Orange in highlights, Teal in shadows
        r = cv2.add(r, 15)
        b = cv2.add(b, -10)
        g = cv2.add(g, 5)
    elif tint_color == "Vintage/Sepia":
        # Standard Sepia Matrix transformation
        matrix = np.array(
            [
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131],
            ]
        )
        graded_img = cv2.transform(graded_img, matrix)
        # Prevent clipping issues after matrix math
        graded_img = np.clip(graded_img, 0, 255).astype("uint8")
        return Image.fromarray(graded_img)

    # Re-merge channels if matrix transformation wasn't used
    graded_img = cv2.merge([r, g, b])
    graded_img = np.clip(graded_img, 0, 255).astype("uint8")

    return Image.fromarray(graded_img)


# --- STREAMLIT UI ---
st.set_page_config(page_title="AI Color Grading Tool", page_icon="🎨", layout="wide")

st.title("🎨 Interactive Image Color Grading Tool")
st.write(
    "Upload any photograph and use the sidebar panel to apply studio-grade color adjustments."
)

# Sidebar Layout for Controls
st.sidebar.header("🎛️ Grading Panel")

uploaded_file = st.sidebar.file_uploader(
    "Choose an image...", type=["jpg", "jpeg", "png"]
)

# Sliders for parameters
brightness = st.sidebar.slider("Brightness (উজ্জ্বলতা)", -100, 100, 0)
contrast = st.sidebar.slider("Contrast (বৈপরীত্য)", 50, 200, 100)
saturation = st.sidebar.slider("Saturation (রঙের ঘনত্ব)", 0, 300, 100)
warm_cool = st.sidebar.slider("Temperature (উষ্ণ / শীতল)", -50, 50, 0)

tint_color = st.sidebar.selectbox(
    "Creative Preset (কালার প্রিসেট)",
    ["None", "Cinematic Teal & Orange", "Vintage/Sepia"],
)

# Main Screen App logic
if uploaded_file is not None:
    # Open the uploaded image
    original_image = Image.open(uploaded_file)

    # Process image dynamically using our function
    processed_image = apply_color_grading(
        original_image, brightness, contrast, saturation, warm_cool, tint_color
    )

    # Setup Side-by-Side comparison columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(original_image, use_container_width=True)

    with col2:
        st.subheader("Color Graded Result")
        st.image(processed_image, use_container_width=True)

        # Download button for the graded image
        # Convert PIL to bytes for delivery
        import io

        buf = io.BytesIO()
        processed_image.save(buf, format="JPEG")
        byte_im = buf.getvalue()

        st.download_button(
            label="💾 Download Graded Image",
            data=byte_im,
            file_name="color_graded_output.jpg",
            mime="image/jpeg",
        )
else:
    st.info("💡 Please upload an image using the sidebar to begin color grading!")