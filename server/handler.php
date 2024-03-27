<?php

echo "hello";


// Check if a file has been uploaded
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['file'])) {
    // The 'file' refers to the key in the files dictionary in your Python script

    $uploadDir = 'audio_outputs/'; // Specify the directory where you want to save the file
    if (!is_dir($uploadDir)) {
        // Attempt to create the folder
        if (mkdir($uploadDir, 0777, true)) {
            echo "Folder created successfully.";
        } else {
            echo "Failed to create the folder.";
        }
    }
    $uploadFile = $uploadDir . basename($_FILES['file']['name']);

    // Check and move the file from the temporary location to the desired directory
    if (move_uploaded_file($_FILES['file']['tmp_name'], $uploadFile)) {
        echo "The file has been uploaded successfully.";
    } else {
        echo "An error occurred while uploading the file.";
    }
} else {
    echo "No file uploaded or wrong HTTP method used.";
}
