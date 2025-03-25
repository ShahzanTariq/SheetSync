import React, { useEffect, useState } from "react";
import { FileInput } from '@mantine/core';
import MasterTable from "./components/masterTable";

const App = () => {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  

  useEffect(() => {
      fetch("http://127.0.0.1:8000/")
          .then((res) => res.json())
          .then((data) => setMessage(data.message))
          .catch((error) => console.error("Error fetching:", error));
  }, []);

  

  const handleFileChange = (inputFile) => {
    const selectedFile = inputFile;
    setFile(selectedFile);
    setFilename(selectedFile.name);
  }

    return (
        <div>
            <h1>React + FastAPI</h1>
            <p>Message from backend: {message}</p>
            
            <FileInput accept=".csv"
              label="Select CSV"
              description="Choose a .csv file to add to master.csv"
              placeholder="ex. td.csv"
              onChange={handleFileChange}
            />

            {filename && <p>Selected file: {filename}</p>}
            <MasterTable/>
        </div>
      );
};

export default App;
