import streamlit as st
import pandas as pd
import io

# Function to convert weight strings to kilograms
def convert_to_kg(weight_str):
    if isinstance(weight_str, str):
        weight_str = weight_str.lower().strip()
        if 'pc' in weight_str:
            # Assumption: An average weight for 'pc' (e.g., Tender Coconut).
            # You might want to refine this based on specific product IDs if possible.
            return 1.2 # Assuming 1.2 kg for '1 pc' product like tender coconut
        elif 'ml' in weight_str:
            try:
                value = float(weight_str.replace('ml', '').strip())
                # Assumption: Density of milk is approx 1.03 g/ml (or 1.03 kg/L)
                return value * 1.03 / 1000  # Convert ml to kg
            except ValueError:
                return None
        elif 'g' in weight_str:
            try:
                value = float(weight_str.replace('g', '').strip())
                return value / 1000  # Convert g to kg
            except ValueError:
                return None
        elif 'kg' in weight_str:
            try:
                return float(weight_str.replace('kg', '').strip())
            except ValueError:
                return None
    return None

# Streamlit App Title
st.set_page_config(layout="wide")
st.title("Product Weight Converter to Kilograms")

st.write("""
Upload your product details file (CSV or Excel) to convert the 'weight' column into kilograms.
""")

# --- Template Download Section ---
st.subheader("1. Download Data Template")
st.write("Click the buttons below to download a template file with the required column headers:")

template_columns = [
    'product_id', 'product_name', 'pack_size', 'bb_order_qty',
    'is_Nonmilk', 'length', 'depth', 'height', 'weight'
]
template_df = pd.DataFrame(columns=template_columns)

# Provide CSV download button for template
csv_template_output = template_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV Template",
    data=csv_template_output,
    file_name='product_data_template.csv',
    mime='text/csv',
    key='csv_template_download'
)

# Provide Excel download button for template
excel_template_output = io.BytesIO()
with pd.ExcelWriter(excel_template_output, engine='xlsxwriter') as writer:
    template_df.to_excel(writer, index=False, sheet_name='ProductData')
excel_template_output.seek(0) # Rewind the buffer
st.download_button(
    label="Download Excel Template",
    data=excel_template_output,
    file_name='product_data_template.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    key='excel_template_download'
)

st.markdown("---")

# --- File Uploader Section ---
st.subheader("2. Upload Your Product Data File")
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

df = None
if uploaded_file is not None:
    # Determine file type and read accordingly
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            df = None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        df = None

    if df is not None:
        st.subheader("3. Original Data (First 5 Rows)")
        st.dataframe(df.head())

        if 'weight' in df.columns:
            st.subheader("4. Converting Weights...")
            # Apply the conversion function
            df['weight_kg'] = df['weight'].apply(convert_to_kg)

            st.subheader("5. Converted Data (with 'weight_kg' column)")
            st.dataframe(df[['product_id', 'product_name', 'pack_size', 'weight', 'weight_kg']].head(10))

            st.subheader("6. Weight Statistics (in kg)")
            st.write(df['weight_kg'].describe())

            # Identify unconvertible entries
            unconverted_count = df['weight_kg'].isnull().sum()
            if unconverted_count > 0:
                st.warning(f"Warning: {unconverted_count} entries in the 'weight' column could not be converted to kg.")
                st.write("Here are some examples of unconvertible entries:")
                st.dataframe(df[df['weight_kg'].isnull()][['product_id', 'product_name', 'weight']].head())

            # Option to download the processed data
            st.subheader("7. Download Converted Data")
            csv_output_converted = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download converted data as CSV",
                data=csv_output_converted,
                file_name='converted_product_weights.csv',
                mime='text/csv',
            )

        else:
            st.error("The uploaded file does not contain a 'weight' column. Please ensure your column is named 'weight' as per the template.")
else:
    st.info("Upload a file to see the conversion results.")

st.markdown("---")
st.markdown("Developed by RK")
