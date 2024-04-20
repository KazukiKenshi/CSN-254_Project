import gtts
import playsound

text = input("Enter Your text here : ")

sound = gtts.gTTS(text, lang="en")

sound.save("file1.mp3")

playsound.playsound("file1.mp3")

