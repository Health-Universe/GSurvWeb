'''GSurvWeb: Open source interactive web application for transplant graft survival prediction

Example:
    To run the streamlit app please use:
        $ streamlit run main.py

    To pass command line options use:
        $ streamlit run main.py -- --h
        $ streamlit run main.py -- --develop

Todo:
    * Update introduction once publication accepted.
'''
# LOAD DEPENDENCY ----------------------------------------------------------
import argparse
import random
import streamlit as st
import pandas as pd

from app.components import interactive
from app.components import experiment
# from app.components import data_summary


# MAIN SCRIPT --------------------------------------------------------------
@st.cache(suppress_st_warning=True)
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            file = pd.read_excel(uploaded_file, sheet_name=None)
            st.sidebar.success('File Uploaded Successfully')
        except UnicodeDecodeError as error:
            st.error(f'error loading log.las: {error}')
        return file, True
    else:
        return None, False

def example_data_download_button():
    st.sidebar.subheader('Example Template')
    st.sidebar.write('Use the provided template as a guide to formatting your data.')
    with open('app/data/example_data_template.xlsx', 'rb') as file:
        st.sidebar.download_button(
            'Download',
            data=file,
            file_name='example_data_template.xlsx',
            help='Click here to download example data',
            )

def reset_session_state(verbose=False):
    '''Resets the session state when app mode changes.
    Session State is an internal Streamlit method used to share variables between reruns.
    '''
    if verbose:
        print(
            f'session status | current mode: {st.session_state["app_mode"]} | '
            f'previous mode: {st.session_state["prev_app_mode"]}'
            )

    if st.session_state['prev_app_mode'] != st.session_state['app_mode']:
        for states in ['continue_state', 'train_state', 'save_state']:
            st.session_state[states] = False
    # update state record
    st.session_state['prev_app_mode'] = st.session_state['app_mode']

def main(dev_mode=False, path_to_local_data='data/example_data_template.xlsx', verbose=False):
    '''main file for running streamlit

    Args:
        dev_mode (bool, optional):
            Takes command line interface based on argparse to run in develop mode.
            Defaults to False.
        path_to_local_data (str, optional):
            Takes command line interface based on argparse to specify path to local
            data to be uploaded for analysis. Only available under develop mode.
            Defaults to 'data/example_data_template.xlsx'.
        verbose (bool, optional):
            Prints detailed sessions status.

    Returns:
        None
    '''
    # Introduction
    st.title('GSurvWeb: Graft survival prediction')
    st.info('❗ The output is not clinically validated. Beta version v0.1.x')
    st.write('This is an open source interactive web application for transplant graft \
        survival prediction designed using Python and Streamlit to help you run \
        basic machine learning algorithms on your dataset')
    st.write('Created by Woochan Hwang (Fy1, Guy\'s and St.Thomas\'). \
        Work submitted for peer review.')

    # Sidebar
    st.sidebar.title('Start Options')
    st.sidebar.write('To begin using the app, load your dataset using \
        the file upload option below.')

    # Load file
    if dev_mode and path_to_local_data is not None:
        uploaded_file = path_to_local_data
    else:
        uploaded_file = st.sidebar.file_uploader(' ', type=['.xlsx'])

    file, upload_status = load_data(uploaded_file)

    if upload_status is False:
        example_data_download_button()
    else:
        # initialize session state
        for states in ['continue_state', 'train_state', 'save_state', 'prev_app_mode']:
            if states not in st.session_state:
                st.session_state[states] = False
        for states in ['app_mode', 'prev_app_mode']:
            if states not in st.session_state:
                st.session_state[states] = 'Interactive'
        # select app mode and refresh session state on change
        if dev_mode:
            app_mode = st.sidebar.selectbox(
                    'Select mode',
                    ['Interactive', 'Experiment', 'Data Summary', 'Develop'],
                    key='app_mode',
                    on_change=reset_session_state(verbose=verbose)
                )
        else:
            app_mode = st.sidebar.selectbox(
                    'Select mode',
                    ['Interactive', 'Experiment', 'Data Summary'],
                    key='app_mode',
                    on_change=reset_session_state(verbose=verbose)
                )
        # run selected app mode
        if app_mode == 'Data Summary':
            # data_summary.data_summary(file)
            st.write('Data Summary is currently deactivated due to issues with pandas profiling and pydantic version')
        elif app_mode == 'Interactive':
            interactive.interactive(file, verbose=verbose)
        elif app_mode == 'Experiment':
            experiment.experiment(file, verbose=verbose)
        elif app_mode == 'Develop':
            dev.dev(file, verbose=verbose)


if __name__ == '__main__':
    random.seed(2021)
    # custom command line options using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--develop',
        action='store_true',
        help='run developer mode with beta features included')
    parser.add_argument(
        '-p', '--path_to_data',
        action='store',
        help='provide path to data in development mode via CLI')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print detailed status on command line')
    args = parser.parse_args()
    print(f'Running command line arguments: {vars(args)}')

    if args.develop:
        from app.components import dev
        main(dev_mode=True, path_to_local_data=args.path_to_data, verbose=args.verbose)
    else:
        assert args.path_to_data is None, 'please use --develop option to specify path'
        main(dev_mode=False, verbose=args.verbose)
