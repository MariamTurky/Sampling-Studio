################################## Essential imports ######################################################
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.express as px
from numpy import sin, pi
import plotly.graph_objects as go
################################## Page Layouts ######################################################
st.set_page_config(
    page_title="Sampling Dashboard",
    page_icon="✅",
    layout="wide",
)
################################## Page construction ######################################################
#Adding css file to webpage
with open("design.css")as f:
    st.markdown(f"<style>{f.read() }</style>",unsafe_allow_html=True)
#Add title
st.title("Sampling Studio For Biological Signals")
st.markdown(" Welcome To Our Sampling Studio ")
st.sidebar.title("Sampling Settings")
#Add elements to side bar
    #select box used to determine type pf provided signals
selected_signal = st.sidebar.selectbox('Provided Signals', ['Generate A Random Signal', 'EMG Sample Signal', 'Generate sine '])
    #slider to provide maximum frequency of signal for sampling process
def set_slider(max_freq):
        user_selected_sampling_frequency = st.sidebar.slider('Change Sampling Maximum Frequency ', 1,max_freq )
        return user_selected_sampling_frequency
#global_variables
layout=st.sidebar.columns(2)
graph1, graph2 = st.columns((1, 1))
col3,col4=st.columns((3,1))
col1, col2 = st.columns(2)
graph3,graph4=st.columns((26,27))
################################## Adding variables to session ######################################################
if 'list_of_signals' not in st.session_state:
    st.session_state['list_of_signals']=[]
    st.session_state['sum_of_signals']=np.zeros(1000)
    st.session_state['sum_of_signals_clean']=np.zeros(1000)
    st.session_state['fig_sine']=go.Figure()
################################## global variables  ######################################################
#cash using(mini memory for the front end)
@st.cache(persist=True)
################################## Function implementation  ######################################################
################################################################################################################################################
#Read and load data to be plotted function
def load_data(select, uploaded_file=None):
    if select == "EMG Sample Signal":
        column_names = ['time', 'values']
        returned_signal = pd.read_csv('EMG.csv', sep = ',', names = column_names, skiprows= 50, skipfooter = 50)
    elif select =="Provide A Local File Signal":
        column_names = ['time','value','frequency','amplitude','phase']
        returned_signal = pd.read_csv(uploaded_file, sep = ',', names = column_names,header=0)
    return returned_signal
#generating a Random signal function
def generate_signal(sample_time_domain):
    F1 = 2
    F2 = 6
    randomly_generated_signal =(2*np.sin(2*np.pi*F1*sample_time_domain)) + (4*np.sin(2*np.pi*F2*sample_time_domain))
    # #Adding Guassian Noise
    # randomly_generated_signal += (np.random.randn(time_domain.size))
    random_signal_dataframe = pd.DataFrame(data = [np.array(sample_time_domain),np.array(randomly_generated_signal)]).T
    random_signal_dataframe.columns = ['time', 'values']
    return random_signal_dataframe
################################################################################################################################################
# Noise function 
def signal_sampling(input_signal, sampling_frequency):
  min_time = np.min(input_signal['time'])
  max_time = np.max(input_signal['time'])
  sampled_signal_time_domain = np.arange(min_time, max_time, 0.5/sampling_frequency)
  sampled_signal_points =np.sin( 2*np.pi* sampling_frequency* sampled_signal_time_domain)
  return sampled_signal_points, sampled_signal_time_domain
################################################################################################################################################
# interpolating function with sinc
def sinc_interp(input_signal, sampling_time):
    original_signal_amplitude = input_signal['values']
    original_signal_time_domain = input_signal['time']
    if len(original_signal_amplitude) != len(original_signal_time_domain):
        raise Exception
    # Find the period
    Time_period = original_signal_time_domain[1] - original_signal_time_domain[0]
    sincM = np.tile(sampling_time, (len(original_signal_time_domain), 1)) - np.tile(original_signal_time_domain[:, np.newaxis], (1, len(sampling_time)))
    resampled_signal = np.dot(original_signal_amplitude, np.sinc(sincM/Time_period))
    # resampled_signal_dataframe = pd.DataFrame(data = [np.array(original_signal_time_domain),np.array(resampled_signal)]).T
    # resampled_signal_dataframe.columns = ['time', 'values']
    return resampled_signal
################################################################################################################################################
# Noise function
def createNoise(SNR,signal_input ):
    Signal_volt=signal_input['values']
    # calculate power in watto off signal
    Signal_power=Signal_volt**2
    # calculate avarage power of signal
    Signal_avg_power=np.mean(Signal_power)
    # change signal into db
    signal_avg_db = 10 * np.log10(Signal_avg_power)
    # Calculate noise according to [2] then convert to watts
    noise_avg_db = signal_avg_db - SNR
    noise_avg_power = 10 ** (noise_avg_db / 10)
    # Generate an sample of white noise
    mean_noise = 0
    #Generate random guassian noise
    noise_volts = np.random.normal(mean_noise, np.sqrt(noise_avg_power), len(Signal_volt))
    #return noisy signal
    return noise_volts+Signal_volt, signal_input['time']
################################################################################################################################################
#function used to clear all ploted sine signals
def clear_data():
    #assign all values to zero
    st.session_state['list_of_signals']=[]
    st.session_state['sum_of_signals']=np.zeros(1000)
    st.session_state['sum_of_signals_clean']=np.zeros(1000)
    st.session_state['fig_sine']=go.Figure()
################################################################################################################################################
#function used to delete signals from the plot
def delete(index_to_delete):
    #get the values that make up the signal to be deleted from list then delete it
    delete_frequency= st.session_state.list_of_signals[index_to_delete][0] #get frequency of  signal to be deleted
    delete_amplitude=st.session_state.list_of_signals[index_to_delete][1]#get frequency of  signal to be deleted
    delete_phase=st.session_state.list_of_signals[index_to_delete][2]#get phase of  signal to be deleted
    st.session_state.list_of_signals.pop(index_to_delete)#remove the ddesired signal parameter from session state
    #turn the tuple data of the figure into list and back to be able to remove the figure of the signal from plot
    list_fig_sine_data=list(st.session_state.fig_sine.data)
    list_fig_sine_data.remove(st.session_state.fig_sine.data[index_to_delete])
    st.session_state.fig_sine.data=tuple(list_fig_sine_data)
    #remove the signal from the summation of sine signals
    removed_signal = delete_amplitude * sin(2 * pi * delete_frequency* time + delete_phase*pi/180)
    st.session_state.sum_of_signals-=removed_signal
    #if there's no remaing signals clear the data
    if not st.session_state.list_of_signals:
        clear_data()
#################################################################################################################################################   
#adding the noise function
def noise_sine():
    #if the value of the SNR is zero then there is no noise in the signal 
    if st.session_state.noise_slider_key==0:
        st.session_state.sum_of_signals=st.session_state.sum_of_signals_clean
        sine_signal_dataFrame=pd.DataFrame(data = [np.array(time),np.array(st.session_state.sum_of_signals)]).T
        sine_signal_dataFrame.columns=['time','values']
        sampled_signal_points, sampled_signal_time_domain = signal_sampling(sine_signal_dataFrame, sampling_frequecny_applied)
        interpolated_signal= sinc_interp(sine_signal_dataFrame, sampled_signal_time_domain)
        resample_signal_plot = px.line(interpolated_signal)
        
    else:
        #add noise to summation of signals
        noise_signal_dataFrame=pd.DataFrame(data = [np.array(time),np.array(st.session_state.sum_of_signals_clean)]).T
        noise_signal_dataFrame.columns=['time','values']
        st.session_state.sum_of_signals,time_noise_domain=createNoise(st.session_state.noise_slider_key, noise_signal_dataFrame ) 
        sine_noise_dataFrame=pd.DataFrame(data = [np.array(time_noise_domain),np.array(st.session_state.sum_of_signals)]).T
        sine_noise_dataFrame.columns=['time','values']
        sampled_signal_points, sampled_signal_time_domain = signal_sampling(sine_noise_dataFrame, sampling_frequecny_applied)
        interpolated_signal= sinc_interp(sine_noise_dataFrame, sampled_signal_time_domain)
        #resample_signal_plot = px.line(interpolated_signal)
        
######################################################################################################################################################
#converting the the signals indvidually and the sum of the signals into a csv file function
def convert_data_to_csv():
    #dataframe of the phases, frequencies and amplitudes of the signals
    df_of_signals=pd.DataFrame(st.session_state.list_of_signals,columns=['Frequency','Amplitude','Phase'])
    #dataframe of the sum of the signals
    df_sum_signals=pd.DataFrame({"Time": time, "Value": st.session_state.sum_of_signals})
    #add both of the data frames and the sum together horizontally
    csv_file=pd.concat([df_sum_signals,df_of_signals],axis=1)
    return csv_file.to_csv(index=False)
################################## Ploting functions ######################################################
################################################################################################################################################
# function used to update used for ploting different sine waves
def update_plot(fig):
    #updating plot layout by changing color ,adding titles to plot ....
    fig.update_layout(
    autosize=False,
    width=500,
    height=500,
    title_text="Generated Sin Waves",
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
    paper_bgcolor="white",
    font_color="black",
)
    #ploting wave using plotly
    st.plotly_chart(fig,use_container_width=True)
################################################################################################################################################
#function used to add each sine wave generated to the same plot
def add_to_plot(fig,x,y,name):
        fig.add_trace(
        go.Scatter(x=x, y=y, name=name)
    ) 
################################################################################################################################################      
#function used to plot the addation  of sin signal generated
def update_sum_plot(x,y): 
    df=pd.DataFrame(dict(x=x,y=y))
    fig=(px.line(df,x='x', y='y'))
    #update layout 
    fig.update_layout(
    autosize=False,
    width=500,
    height=500,
    title_text="Addition of Sin Waves",
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
    paper_bgcolor="white",
    font_color="black",
)
    st.plotly_chart(fig,use_container_width=True)



################################## Main implementation ######################################################
if selected_signal == "Generate A Random Signal":
    sampling_frequecny_applied = set_slider(100)
    random_signal = generate_signal(np.linspace(0,1, 1000))
    SNR= st.sidebar.slider('SNR', 0, 20,0,key='SNR')
    if SNR==0 :
        origianal_signal_plot = px.line(random_signal, x = random_signal['time'], y = random_signal['values'])
        sampled_signal_points, sampled_signal_time_domain = signal_sampling(random_signal, sampling_frequecny_applied)
        interpolated_signal= sinc_interp(random_signal, sampled_signal_time_domain)
        resample_signal_plot = px.line(interpolated_signal)
        with graph1:
            st.plotly_chart(origianal_signal_plot, use_container_width=True, height = 100, width = 100)
        with graph2:
            st.plotly_chart(resample_signal_plot,  use_container_width=True, height = 100, width = 100)
    else:
        noised_signal,time_domain=createNoise(SNR,random_signal)
        noised_signal_dataFrame=pd.DataFrame(data = [np.array(time_domain),np.array(noised_signal)]).T
        noised_signal_dataFrame.columns=['time','values']
        sampled_signal_points, sampled_signal_time_domain = signal_sampling(noised_signal_dataFrame, sampling_frequecny_applied)
        interpolated_signal = sinc_interp(noised_signal_dataFrame, sampled_signal_time_domain)
        fig_resample = px.line(interpolated_signal)
        noise_fig = px.line(x=time_domain,y=noised_signal)
        with graph1:
            st.plotly_chart(noise_fig,use_container_width=True)
        with graph2:
            st.plotly_chart(fig_resample,use_container_width=True)

elif selected_signal == "EMG Sample Signal":
    emg = load_data(selected_signal)
    emg = emg[0:1001]
    sampling_frequecny_applied = set_slider(400)
    #slider to get signal to noise ratio
    SNR= st.sidebar.slider('SNR', 0, 20,0,key='SNR')
    if SNR==0 :
        origianal_signal_plot = px.line(emg, x = emg['time'], y = emg['values'])
        sampled_signal_points, sampled_signal_time_domain = signal_sampling(emg, sampling_frequecny_applied)
        interpolated_signal= sinc_interp(emg, sampled_signal_time_domain)
        resample_signal_plot = px.line(interpolated_signal)
        with graph1:
            st.plotly_chart(origianal_signal_plot, use_container_width=True, height = 100, width = 100)
        with graph2:
            st.plotly_chart(resample_signal_plot,  use_container_width=True, height = 100, width = 100)
    else:
        emg_m=np.array(emg)
        noised_signal,emg_time=createNoise(SNR,emg)
        noised_signal_dataFrame=pd.DataFrame(data = [np.array(emg_time),np.array(noised_signal)]).T
        noised_signal_dataFrame.columns=['time','values']
        sampled_signal_points, sampled_signal_time_domain = signal_sampling(noised_signal_dataFrame, sampling_frequecny_applied)
        interpolated_signal = sinc_interp(noised_signal_dataFrame, sampled_signal_time_domain)
        fig_resample = px.line(interpolated_signal)
        noise_fig=px.line(x=emg_time,y=noised_signal)
        with graph1:
            st.plotly_chart(noise_fig,use_container_width=True)
        with graph2:
            st.plotly_chart(fig_resample,use_container_width=True)

elif selected_signal == 'Generate sine ':
    time = np.linspace(0, 5, 1000)
    with st.sidebar:
        #slider to get frequency for sin wave generation
        frequency = st.slider('Frequency', 0.0, 20.0, step=0.5, key='Frequency')
        #slider to get amplitude for sin wave generation
        amplitude = st.slider('Amplitude', 0, 20, 0, key='Amplitude')
        #slider to get phase for sin wave generation
        phase = st.slider('Phase', 0, 360, 0, key='Phase')
    genrate_button=st.sidebar.button('Genrate Sin',key=0)
        #initialize_plot(st.session_state.fig_sine)
    sampling_frequecny_applied = set_slider(400)
    if genrate_button:
        #calculate the sin of the values retrived then draw it
        sine_volt = amplitude * sin(2 * pi * frequency * time + phase*pi/180)
        add_to_plot(st.session_state.fig_sine,x=time,y=sine_volt,name=f"{frequency}hz") 
        #add the signal to the cache storage
        signal_parameters=[frequency,amplitude,phase]
        st.session_state.list_of_signals.append(signal_parameters)
        st.session_state.sum_of_signals+=sine_volt
        st.session_state.sum_of_signals_clean=st.session_state.sum_of_signals
    #UPLOADING A GENRATED FILE
    with graph4:
        uploaded_file = st.file_uploader("Please choose a CSV or TXT file", accept_multiple_files=False,type=['csv','txt'])

        #add a button to add uploaded file
    with graph4:
        add_upload=st.button('Add file')
            #if there's a file uploaded and the button is pressed
        if uploaded_file and add_upload :
                #download the data to the browser
                data=load_data( 'Provide A Local File Signal',uploaded_file)
                #get the signal parameters and remove the empty entries
                amplitudes_of_downloaded_signal=np.array(data.amplitude.dropna())
                frequencies_of_downloaded_signal=np.array(data.frequency.dropna())
                phases_of_downloaded_signal=np.array(data.phase.dropna())
                t=np.array(data.time)
                #loop through the present values of the frequencies
                for i in range(len(frequencies_of_downloaded_signal)):
                    #calculate the sine and draw it 
                    sine_volt = amplitudes_of_downloaded_signal[i] * sin(2 * pi * frequencies_of_downloaded_signal[i] * t + phases_of_downloaded_signal[i]*pi/180)
                    add_to_plot(st.session_state.fig_sine,x=t,y=sine_volt,name=f"{frequencies_of_downloaded_signal[i]}hz")
                    #add the parameters to the stored data 
                    signal_parameters=[frequencies_of_downloaded_signal[i],amplitudes_of_downloaded_signal[i],phases_of_downloaded_signal[i]]
                    st.session_state.list_of_signals.append(signal_parameters)
            
            #add the values(y-axis) to the stored sum
                st.session_state.sum_of_signals+=data.value
                st.session_state.sum_of_signals_clean=st.session_state.sum_of_signals
    
    if st.session_state.list_of_signals:
        option = st.sidebar.selectbox(
        'Select Values to Delete',
        st.session_state.list_of_signals,format_func=lambda x: "Frequency:" + str(x[0])+", Amplitude:" + str(x[1])+", Phase:" + str(x[2]))
        selected_value=st.session_state.list_of_signals.index(option)
        with col2:
            #if the button is pressed go the delete function
            delete_button=st.sidebar.button('delete',key=1,on_click=delete,args= (selected_value,))
        #if the slider of the noise changes then go noise func
        noise_sin=st.sidebar.slider('SNR sine',key="noise_slider_key",on_change=noise_sine)  
        #after every change from the upload, delete or genrate we update both plots
    with col1:
        update_plot(st.session_state.fig_sine)
    with col2:
        update_sum_plot(x=time,y=st.session_state.sum_of_signals)
    sine_signal_dataFrame=pd.DataFrame(data = [np.array(time),np.array(st.session_state.sum_of_signals)]).T
    sine_signal_dataFrame.columns=['time','values']
    sampled_signal_points, sampled_signal_time_domain = signal_sampling(sine_signal_dataFrame, sampling_frequecny_applied)
    interpolated_signal= sinc_interp(sine_signal_dataFrame, sampled_signal_time_domain)
    resample_signal_plot = px.line(interpolated_signal)  
    with graph3:   
        st.plotly_chart(resample_signal_plot,  use_container_width=True, height = 100, width = 100)
    with layout[0]:
        st.download_button(
            label="Save ",
            data=convert_data_to_csv(),
            file_name='large_df.csv',
            mime='text/csv',
        )
    with layout[-1]:
        st.button("Clear",on_click=clear_data)