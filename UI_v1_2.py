import os
import streamlit as st
import pandas as pd
from core_functions_v1_2 import perform_univariate_analysis, perform_bivariate_analysis, perform_multivariate_analysis, \
    write_output_to_excel

# Define the main function for the UI
def main():
    st.title("Exploratory Data Analysis Tool")
    # User selects the input type: CSV file or Database connection
    input_type = st.radio("Select Input Type", ("CSV File", "Database Connection"))
    # If CSV File is selected
    if input_type == "CSV File":
        st.subheader("CSV File Input")
        csv_file = st.file_uploader("Upload CSV File", type=["csv"])
        if csv_file is not None:
            data = pd.read_csv(csv_file)
            st.success("CSV File successfully loaded.")
        else:
            st.warning("Please upload a CSV file.")

    # If Database Connection is selected
    elif input_type == "Database Connection":
        st.subheader("Database Connection Input")
        db_connection = st.text_input("Database Connection String")
        db_query = st.text_area("Enter SQL Query")
        if st.button("Fetch Data"):
            if db_connection and db_query:
                # Code to fetch data from the database using db_connection and db_query
                # Replace the code below with your database fetching logic
                data = pd.DataFrame()  # Replace this with the fetched data
                st.success("Data successfully fetched from the database.")
            else:
                st.warning("Please enter a valid Database Connection String and SQL Query.")
    else:
        st.error("Invalid Input Type selected.")

    if 'data' in locals():
        # Section for univariate analysis
        st.header("Univariate Analysis")
        # Get user inputs for column selection
        selected_columns_univariate = st.multiselect("Select Columns for Univariate Analysis", data.columns, default=list(data.columns))
        # Perform univariate analysis
        if st.button("Analyze Univariate and Show"):
            univariate_output = perform_univariate_analysis(data, selected_columns_univariate)
            # Display the analysis output on a separate web page
            for output in univariate_output:
                column = output["column"]
                plot = output["plot"]
                #st.plotly_chart(output["plot"])
                # Create a separate container for each output
                new_page = st.empty()
                with new_page:
                    st.plotly_chart(plot)

       # univariate_output = perform_univariate_analysis(data, selected_columns_univariate)

        # Display univariate analysis plots
        #for output in univariate_output:
        #    st.write(f"### {output['column']}")
        #    st.plotly_chart(output['plot'])
        elif st.button("Save Univariate Analysis Output"):
            # Perform univariate analysis
            univariate_output = perform_univariate_analysis(data, selected_columns_univariate)
            # Write the analysis output to an Excel file
            write_output_to_excel(univariate_output, "univariate_analysis_output.xlsx")
            st.success("Univariate analysis output saved to 'univariate_analysis_output.xlsx'")

        # Section for bivariate analysis
        st.header("Bivariate Analysis")
        # Get user inputs for column selection
        selected_columns_bivariate = st.multiselect("Select Columns for Bivariate Analysis", data.columns)
        # Perform bivariate analysis
        if st.button("Analyze Bivariavte and Show"):
            bivariate_output = perform_bivariate_analysis(data, selected_columns_bivariate)
            # Display bivariate analysis plots
            for output in bivariate_output:
                st.plotly_chart(output["plot"])
        elif st.button("Save Bivariate Analysis Output"):
            # Perform univariate analysis
            bivariate_output = perform_bivariate_analysis(data, selected_columns_bivariate)
            # Write the analysis output to an Excel file
            write_output_to_excel(bivariate_output, "Bivariate_analysis_output.xlsx")
            st.success("Bivariate analysis output saved to 'Bivariate_analysis_output.xlsx'")

        # Section for multivariate analysis
        st.header("Multivariate Analysis")
        # Get user inputs for column selection
        selected_columns_multivariate = st.multiselect("Select Columns for Multivariate Analysis", data.columns)
        # Perform multivariate analysis
        if st.button("Analyze Multivariavte and Show"):
            multivariate_output = perform_multivariate_analysis(data, selected_columns_multivariate)
            for output in multivariate_output:
                st.plotly_chart(output["plot"])
        elif st.button("Save Multivariate Analysis Output"):
            multivariate_output = perform_multivariate_analysis(data, selected_columns_multivariate)
            write_output_to_excel(multivariate_output, "Multivariate_analysis_output.xlsx")
            st.success("Multivariate analysis output saved to 'Multivariate_analysis_output.xlsx'")


# Call the main function
if __name__ == "__main__":
    main()
