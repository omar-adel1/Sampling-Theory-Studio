import numpy as np
import pandas as pd
from Signal_Class import Signal
import plotly.express as px


#________Initializing variables_______#
signal_default_time = np.arange(0,1,0.001)    #1000 default samples for the time axis   


signal_default_values = np.zeros(len(signal_default_time))    

max_frequency = 1   

Final_signal_sum = None       

total_signals_list = [Signal(amplitude=1,frequency=1,phase=0)]  #contains all individual signals (freq components) forming the final or resulted signal   

signals_uploaded_list = []

generate_sine_signal =  None

snr_value = 50       



#__________Main Functions_______#

#Continue 
def generate_noisy_signal(snr_level):
    
    #Generates a noisy signal with a controllable SNR level.
    
    #Args:
     #   snr_level (float): The desired SNR level in dB.
    #Returns:
      #noisy_signal (ndarray): The generated noisy signal.
      
 
      
    temp_signal = Final_signal_sum 
    signal_mean = np.mean(temp_signal)
     
    
    # Generate the signal
   # time = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    
    # Calculate the power of the signal
    signal_power = np.sum((temp_signal-signal_mean) ** 2) / len(temp_signal)
    
    # Calculate the noise power based on the desired SNR level
    linear_ratio = 10 ** (snr_level / 10)  # Convert dB to power ratio
    noise_power = signal_power / linear_ratio 
    
    # Generate white noise with the same length as the signal
    noise = np.random.normal(0,np.sqrt(noise_power), size=len(temp_signal))
    
  
    return noise
  
 
def generateFinalSignal(noise_flag,signal_uploaded_browser,SNR=40):
    """
    This function checks if there is an uploaded signal from browser and checks if there is added
    noise, it then adds all signals (mixer,browser,noise) and generates a final signal.
    
    noise_flag:bool check if there is noise added
    signal_uploaded_browser: uploaded signal from browser
    SNR: Signal-to-noise ratio
    """
    
    global Final_signal_sum
    
    if signal_uploaded_browser is not None:
        
        temp_final_signal = signal_uploaded_browser.copy()        
    else:
        temp_final_signal = signal_default_values.copy()          
              
    
    for signal in total_signals_list:      
        temp_final_signal+=signal.amplitude*np.sin(signal.frequency*2*np.pi*signal_default_time + signal.phase* np.pi )
    
    
    if noise_flag:
        Final_signal_sum = temp_final_signal + generate_noisy_signal(SNR)   
    
    else:
        Final_signal_sum = temp_final_signal
      
    
    return pd.DataFrame(Final_signal_sum,signal_default_time)


def interpolate(time_new, signal_time, signal_amplitude):
    """
        Sinc Interpolation
        Parameters
        ----------
        time_new : array of float
            new time to smple at
        signal_time : array of float
            samples of time
        signal_amplitude : array of float
            amplitudes at signal_time 
        Return
        ----------
        new_Amplitude : array of float
            new amplitudes at time_new
            
        ## Interpolation using the whittaker-shannon interpolation formula that sums shifted and weighted sinc functions to give the interpolated signal
        ## Each sample in original signal corresponds to a sinc function centered at the sample and weighted by the sample amplitude
        ## summing all these sinc functions at the new time array points gives us the interploated signal at these points.     
    """


    # sincM is a 2D matrix of shape (len(signal_time), len(time_new))
    # By subtracting the sampled time points from the interpolated time points
    
    sincMatrix = np.tile(time_new, (len(signal_time), 1)) - np.tile(signal_time[:, np.newaxis], (1, len(time_new)))
  
    # sinc interpolation 
    #This dot product results in a new set of amplitude values that approximate the original signal at the interpolated time points.
    signal_interpolated = np.dot(signal_amplitude, np.sinc(sincMatrix/(signal_time[1] - signal_time[0])))   
    return signal_interpolated



def renderSampledSignal(nyquist_rate, is_normalized_freq):
    """
        render sampled and interpolated signal
        Parameters
        ----------
        nyquist_rate : float
            F_sample/max_frequency
        Return
        ----------
        fig : Figure
            plot of the interpolated sampled signal
        downloaded_df : Dataframe
            the resulted signal to be downloaded
    """
    global max_frequency
    
    
    if is_normalized_freq:

        time = np.arange(0, signal_default_time[-1], 1/(nyquist_rate*max_frequency))  
    else:
        time = np.arange(0, signal_default_time[-1], 1/(nyquist_rate))

    y_samples = interpolate(time, signal_default_time, Final_signal_sum )  #sampling/samples taken with input sampling frequency

    y_interpolated = interpolate(signal_default_time, time, y_samples)   # interploated signal or reconstructed signal
    df = pd.DataFrame(signal_default_time, y_interpolated)

 # Original signal with markers for sampled points
    fig1 = px.scatter(x=time, y=y_samples , labels={"x": "Time (s)", "y": "Amplitude (mv)"}, color_discrete_sequence=['#FAFAFA'])
    fig1['data'][0]['showlegend'] = True
    fig1['data'][0]['name'] = ' Samples '
    fig1.add_scatter(name="Original_Signal", x=signal_default_time, y=Final_signal_sum,line_color = 'blue' )
    fig1.update_traces(marker={'size': 10})
    fig1.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig1.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))
    fig1.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))

    # Reconstructed signal along with sampling points/markers
    fig2 = px.scatter(x=time, y=y_samples , labels={"x": "Time (s)", "y": "Amplitude (mv)"}, color_discrete_sequence=['#FAFAFA'])
    fig2['data'][0]['showlegend'] = True
    fig2['data'][0]['name'] = ' Samples '
    fig2.add_scatter(name="Reconstructed",x=signal_default_time, y=y_interpolated,  line_color="#FF4B4B")
    fig2.update_traces(marker={'size': 10}, line_color="#FF4B4B")
    fig2.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig2.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))
    fig2.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))

    # Difference between original and reconstructed signal
    fig3 = px.scatter(x=time, y=y_samples , labels={"x": "Time (s)", "y": "Amplitude (mv)"}, color_discrete_sequence=['#FAFAFA'])
    fig3['data'][0]['showlegend'] = True
    fig3['data'][0]['name'] = ' Samples '
    fig3.add_scatter(name="Reconstructed",x=signal_default_time, y=y_interpolated,line_color="#FF4B4B")
    fig3.update_traces(marker={'size': 10}, line_color="#FF4B4B")
    fig3.add_scatter(name="Original_Signal",x =signal_default_time,y =Final_signal_sum, line_color='blue' )
    fig3.update_traces(marker={'size': 10})
    fig3.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig3.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))
    fig3.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#5E5E5E', title_font=dict(size=24, family='Arial'))

    return fig1, fig2, fig3,df.drop(df.columns[[0]], axis=1)  # returns 3 figs along with interpolated signal values where each row corresponds to interpolated signal value at specific time point.





def addSignalToList(amplitude, frequency, phase):
    """
    Add signals to added_list
    :param amplitude: the amplitude of the signal
    :param frequency: the frequency of the signal
    :param phase: the phase of the signal
    """
    global max_frequency
    signal = Signal(amplitude=amplitude, frequency=frequency, phase=phase)
    total_signals_list.append(signal)
    max_frequency = max(max_frequency, signal.frequency)


def removeSignalFromList(amplitude, frequency, phase):
    
    """
    remove signals from added_list
    Parameters
    ----------
    amplitude : float
    the amplitude of the signal
    frequency : float
    the frequancy of the signal
    phase : float
    the phase of the signal
    """

    for i in range(len(total_signals_list)):
        if total_signals_list[i].amplitude == amplitude and total_signals_list[i].frequency == frequency and total_signals_list[i].phase == phase:
            total_signals_list.pop(i)
            break

    if max_frequency == frequency:
        SetmaxFreq()


def sinGeneration(amplitude, Freq, phase):
    global generate_sine_signal
    generate_sine_signal=np.sin(2*np.pi*(signal_default_time*Freq)+phase*np.pi)*amplitude
    


def SetmaxFreq(): #set the maximum freq where loops on the signal stored by the user and select the max frequency uploaded by the user
    findMaxFreq=1,
    global max_frequency
    for signals in total_signals_list:
        findMaxFreq=max(findMaxFreq,signals.frequency) 

    max_frequency= findMaxFreq    


def get_Total_signal_list():
    return total_signals_list


def set_snr_level(snr_level):
    global snr_value
    snr_value = snr_level


def get_snr_level():
    global snr_value
    return snr_value 

def Reintialize_values():
    global signal_default_time, max_frequency
    signal_default_time = np.arrange(0,1,0.001)    #1000 default samples for the time axis   
    max_frequency = 1
    
    for signals in  total_signals_list : 
        if signals.frequency > max_frequency:
            max_frequency = signals.frequency
        


#def SignalListClean():
 #   global max_frequency
  #  max_frequency=1
   # total_signals_list.clear()