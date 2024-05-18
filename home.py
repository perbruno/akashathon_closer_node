import streamlit as st
from datetime import datetime

from resources_analysis import ResourceUsage
from user_analysis import get_users_distribution

st.image('static/logo.png')

st.page_link(
    "https://console.akash.network/",
    label="Deploy your application with Akash",
    icon="🚀",
)

if "button" not in st.session_state:
    st.session_state.button = False


def click_button():
    st.session_state.button = True


with st.expander("Input data", expanded=True):
    with st.form("input_data"):
        st.subheader("Instances Resources")

        resources_file = st.file_uploader("Add the csv file related to the resource", key="rsc")

        ram = st.number_input("Memory (gb)", min_value=1, max_value=512, placeholder=None)
        cpu = st.number_input("vCPU", min_value=1, max_value=None, placeholder=None)
        gpu = st.number_input("gpu", min_value=0, max_value=None, placeholder=None)

        """---"""
        st.subheader("Access Logs")
        access_files = st.file_uploader(
            "Add the csv file related to the resource",
            key="user",
            accept_multiple_files=True,
        )

        """---"""
        st.form_submit_button(on_click=click_button)


if st.session_state.button:
    if resources_file is not None:
        with st.spinner("Loading data about the resources..."):
            next_errors = ResourceUsage(resources_file, ram, cpu, gpu)
            dates = "\n\n".join(list(map(str, next_errors.next_value())))
            dd = next_errors.get_akash_providers()
        st.info(f"next fail will happen between:\n\n {dates}", icon="ℹ️")
        st.text("What about try one of the Akash providers to mitigate the issue?")
        st.page_link(
            "https://console.akash.network/providers",
            label="Deploy your application with Akash",
            icon="🚀",
        )
        st.dataframe(dd.to_pandas(),use_container_width=True)

    if access_files is not None:
        with st.spinner("Loading data about user access..."):
            user_data, total_access = get_users_distribution(access_files)
        st.map(user_data)

else:
    pass
