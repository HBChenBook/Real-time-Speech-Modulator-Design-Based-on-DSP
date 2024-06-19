import tkinter as tk
from tkinter import messagebox
import pyaudio
import wave
import numpy as np
import scipy.signal as signal
import soundfile as sf
import threading

# global variable
RECORD_SECONDS = 5
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

class AudioProcessor:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []

    def record_audio(self):
        self.stream = self.p.open(format=FORMAT, channels=CHANNELS,
                                  rate=RATE, input=True,
                                  frames_per_buffer=CHUNK)
        print("开始录音...")
        self.frames = []
        for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
            data = self.stream.read(CHUNK)
            self.frames.append(data)
        print("录音结束")
        self.stream.stop_stream()
        self.stream.close()
        wf = wave.open('output.wav', 'wb') #将录制结果保存为wav文件
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        messagebox.showinfo("Info", "录音完成")

    def play_audio(self, file_path):
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return (data, pyaudio.paContinue)

        wf = wave.open(file_path, 'rb')
        stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                             channels=wf.getnchannels(),
                             rate=wf.getframerate(),
                             output=True,
                             stream_callback=callback)

        stream.start_stream()
        while stream.is_active():
            pass
        stream.stop_stream()
        stream.close()
        wf.close()

    def pitch_shift(self, pitch_factor):
        data, samplerate = sf.read('output.wav')
        indices = np.round(np.arange(0, len(data), pitch_factor))
        indices = indices[indices < len(data)].astype(int)
        shifted_data = data[indices.astype(int)]
        sf.write('pitch_shifted.wav', shifted_data, samplerate)
        messagebox.showinfo("Info", "音高变调完成")

    def speed_shift(self, speed_factor):
        data, samplerate = sf.read('output.wav')
        indices = np.round(np.arange(0, len(data), 1/speed_factor))
        indices = indices[indices < len(data)].astype(int)
        stretched_data = data[indices.astype(int)]
        sf.write('speed_shifted.wav', stretched_data, samplerate)
        messagebox.showinfo("Info", "速度变调完成")

    def filter_noise(self):
        data, samplerate = sf.read('output.wav')
        b, a = signal.iirnotch(50, 30, samplerate)
        filtered_data = signal.filtfilt(b, a, data)
        sf.write('filtered.wav', filtered_data, samplerate)
        messagebox.showinfo("Info", "去除噪音完成")

    def apply_equalizer(self, low_gain, mid_gain, high_gain):
        data, samplerate = sf.read('output.wav')
        nyquist = 0.5 * samplerate
        low = signal.butter(1, 300 / nyquist, btype='low')
        mid = signal.butter(1, [300 / nyquist, 3000 / nyquist], btype='band')
        high = signal.butter(1, 3000 / nyquist, btype='high')
        
        low_filtered = signal.filtfilt(*low, data) * low_gain
        mid_filtered = signal.filtfilt(*mid, data) * mid_gain
        high_filtered = signal.filtfilt(*high, data) * high_gain
        
        equalized_data = low_filtered + mid_filtered + high_filtered
        sf.write('equalized.wav', equalized_data, samplerate)
        messagebox.showinfo("Info", "均衡器处理完成")

def start_recording():
    audio_processor.record_audio()

def start_pitch_shift():
    pitch_factor = float(pitch_factor_entry.get())
    audio_processor.pitch_shift(pitch_factor)

def start_speed_shift():
    speed_factor = float(speed_factor_entry.get())
    audio_processor.speed_shift(speed_factor)

def start_filter_noise():
    audio_processor.filter_noise()

def start_equalizer():
    low_gain = float(low_gain_entry.get())
    mid_gain = float(mid_gain_entry.get())
    high_gain = float(high_gain_entry.get())
    audio_processor.apply_equalizer(low_gain, mid_gain, high_gain)

def start_play_audio(file_path):
    threading.Thread(target=audio_processor.play_audio, args=(file_path,)).start()

audio_processor = AudioProcessor()

# GUI setup
root = tk.Tk()
root.title("语音信号处理")

record_button = tk.Button(root, text="录音", command=start_recording)
record_button.grid(row=1,column=1)
play_output_button = tk.Button(root, text="播放录音", command=lambda: start_play_audio('output.wav'))
play_output_button.grid(row=2,column=1)
pitch_factor_label = tk.Label(root, text="音高变调因子(音高变高倍数):")
pitch_factor_label.grid(row=3,column=1)
pitch_factor_entry = tk.Entry(root)
pitch_factor_entry.grid(row=4,column=1)
pitch_shift_button = tk.Button(root, text="应用音高变调", command=start_pitch_shift)
pitch_shift_button.grid(row=4,column=2)
play_pitch_shifted_button = tk.Button(root, text="播放音高变调录音", command=lambda: start_play_audio('pitch_shifted.wav'))
play_pitch_shifted_button.grid(row=4,column=3)

speed_factor_label = tk.Label(root, text="速度变调因子(变慢倍数):")
speed_factor_label.grid(row=5,column=1)
speed_factor_entry = tk.Entry(root)
speed_factor_entry.grid(row=6,column=1)
speed_shift_button = tk.Button(root, text="应用速度变调", command=start_speed_shift)
speed_shift_button.grid(row=6,column=2)
play_speed_shifted_button = tk.Button(root, text="播放速度变调录音", command=lambda: start_play_audio('speed_shifted.wav'))
play_speed_shifted_button.grid(row=6,column=3)

filter_noise_button = tk.Button(root, text="去除噪音", command=start_filter_noise)
filter_noise_button.grid(row=7,column=1)
play_filtered_button = tk.Button(root, text="播放去噪音录音", command=lambda: start_play_audio('filtered.wav'))
play_filtered_button.grid(row=8,column=1)

low_gain_label = tk.Label(root, text="低频增益:")
low_gain_label.grid(row=9,column=1)
low_gain_entry = tk.Entry(root)
low_gain_entry.grid(row=10,column=1)
mid_gain_label = tk.Label(root, text="中频增益:")
mid_gain_label.grid(row=11,column=1)
mid_gain_entry = tk.Entry(root)
mid_gain_entry.grid(row=12,column=1)
high_gain_label = tk.Label(root, text="高频增益:")
high_gain_label.grid(row=13,column=1)
high_gain_entry = tk.Entry(root)
high_gain_entry.grid(row=14,column=1)
equalizer_button = tk.Button(root, text="应用均衡器", command=start_equalizer)
equalizer_button.grid(row=14,column=2)
play_equalized_button = tk.Button(root, text="播放均衡器处理录音", command=lambda: start_play_audio('equalized.wav'))
play_equalized_button.grid(row=14,column=3)

root.mainloop()