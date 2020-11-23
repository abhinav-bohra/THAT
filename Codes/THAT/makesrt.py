import pysrt
import speech_recognition as sr
import srt
import time 
import soundfile as sf
def makesrt():
    filename="video.wav"
    subs=[]
    text=[]
    audio_file = sr.AudioFile(filename)
    i=1
    f = sf.SoundFile(filename)
    total_time=float(format(len(f) / f.samplerate))
    r = sr.Recognizer()
    start_time=0
    end_time=0
    while((i-1)*5<total_time) : 
        start_time=end_time
        end_time=end_time+5
        with audio_file as source:
            audio = r.record(source,offset=(i-1)*5,duration=5)  # read the 5sec audio file
        # recognize speech using Google Speech Recognition Library
        try:
            text= r.recognize_google(audio)
            
            text="'''\\\n"+str(i)+"\n"+time.strftime('%H:%M:%S', time.gmtime(start_time))+",0 --> "+time.strftime('%H:%M:%S', time.gmtime(end_time))+",0\n"+text+"\n\n"+"'''"
            print(text)
            #text=to_srt(text)
            k=srt.parse(text,ignore_errors=False) 
            subs.append(k)
            
        except sr.UnknownValueError:
            print()
        except sr.RequestError as e:
            #return "Could not request results from Speech Recognition service; {0}".format(e)
            print("Could not understand audio : "+e)   
            break
        i=i+1
    srt.compose(subs)
    print(subs)
    return text
print(makesrt())