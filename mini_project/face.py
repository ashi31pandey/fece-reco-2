import cv2
import numpy as np
import re
import os
import time
import csv
import json
from tkinter import *
from tkinter import messagebox
from tkinter import Tk, Label, Entry, Button, PhotoImage
from PIL import Image, ImageTk

def resize_image(image_path, width, height):
    original_image = Image.open(image_path)
    resized_image = original_image.resize((width, height))
    return ImageTk.PhotoImage(resized_image)

def create_gui():
    root = Tk()
    root.title("Face Recognition Attendance System")
    root.geometry('500x500')
    
    target_width = 500
    target_height = 300
    image_path = r"D:\PERSONAL\ashish\CLG STD\ashish project\project_cllg\fece reco 2\mini_project\giphy.gif"
    resized_image = resize_image(image_path, target_width, target_height)

    def capture_images():
        name = name_entry.get()
        roll = roll_entry.get()
        student_data = get_student_data(name,roll)
        try:
            with open('data.json','r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
            
        data.append(student_data)

        with open("data.json", "w") as file:
            json.dump(data, file, indent=2)
        capture(name, roll)
        messagebox.showinfo("Success", "Images captured successfully!")

    def mark_attendance():
        markAttendance()
        messagebox.showinfo("Success", "Attendance marked successfully!")
    
    label_image = Label(root, image=resized_image)
    label_name = Label(root, text="Enter student name:")
    label_roll = Label(root, text="Enter roll number:")
    name_entry = Entry(root)
    roll_entry = Entry(root)

    capture_button = Button(root, text="Capture Images", command=capture_images)
    mark_button = Button(root, text="Mark Attendance", command=mark_attendance)
    
    label_image.grid(row=0, column=0, columnspan=2)
    label_name.grid(row=1, column=0)
    name_entry.grid(row=1, column=1)
    label_roll.grid(row=2, column=0)
    roll_entry.grid(row=2, column=1)
    capture_button.grid(row=3, column=0, columnspan=2, pady=10)
    mark_button.grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()

def get_student_data(name,roll_number):
    return {roll_number: name}

def find_student_name(roll_number,data):
    for student in data:
        if roll_number in student:
            return student[roll_number]
    return None

def get_name_by_roll(label):
    try:
        with open('data.json','r') as file:
            data = json.load(file)
        student_name = find_student_name(label, data)
        if student_name is not None:
            return student_name
        else:
            return None
    except FileNotFoundError:
        print("No Student data found")

def load_image_from_folder(folder):
    faces = []
    labels = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            label = re.findall(r'\d+',filename)
            if label:
                label = int(label[0])
                faces.append(img)
                labels.append(label)
    return faces, labels

def capture(name , roll):
    student_details = {}
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')    
    cap = cv2.VideoCapture(0)

    count = 0
    max_images_per_student = 5

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for(x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            cv2.rectangle(frame,(x,y),(x + w , y + h), (0, 255, 0), 3)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                if count < max_images_per_student:
                    img_name = f"{roll}_{count}.png"
                    img_path = os.path.join('student_data', img_name)
                    cv2.imwrite(img_path, roi_gray)
                    student_details[img_name] = name

                    count += 1
                    print(f"Image {count} captured for {name}")

                    if count == max_images_per_student:
                        count = 0
                else:
                    print("Maximum images are already captured for this student")        
    
        cv2.imshow('Capture Images for Students', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    roll = int(roll) + 1
    cap.release()
    cv2.destroyAllWindows()

def markAttendance():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    folder_path = r"D:\PERSONAL\ashish\CLG STD\ashish project\project_cllg\fece reco 2\mini_project\student_data"
    stored_faces, labels = load_image_from_folder(folder_path)
    recognizer.train(stored_faces, np.array(labels))
    
    student_details = {}
    for filename in os.listdir('student_data'):
        label = re.findall(r'\d+', filename)
        if label:
            label = int(label[0])
            student_details[filename] = f"Student_{label}"

    capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    count = 0
    confirm = 0

    cv2.namedWindow('Face Recognition', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Face Recognition', 800, 600)

    print("Get ready, the camera will start in 3 seconds...")
    time.sleep(3)

    csv_file_path = 'attendance.csv'
    file_exists = os.path.exists(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['Roll No.', 'Name', 'Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        while True:
            ret, frame = capture.read()
            if not ret:
                print("Image not read properly")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in faces:
                face = gray[y:y + h, x:x + w]
                label, confidence = recognizer.predict(face)

                threshold = 70
                if confidence < threshold:
                    print("Match found")
        
                    name = get_name_by_roll(str(label))
                    confirm = 3
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow({'Roll No.': label, 'Name': str(name), 'Timestamp': timestamp})
                    break

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            if confirm == 3 or count == 50:
                break

            cv2.imshow('Face Recognition', frame)
            count += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    capture.release()
    cv2.destroyAllWindows()

    if not confirm:
        print("Not in the database")

if __name__ == "__main__":
    data_dir = 'student_data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    create_gui()


                   
