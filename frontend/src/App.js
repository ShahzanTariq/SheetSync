import React, { useEffect, useState } from "react";
import { FileInput, Select, Group, Button } from '@mantine/core';
import MasterTable from "./components/masterTable";

const App = () => {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [card, setCard] = useState("");
  

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error("Error fetching:", error));
  }, []);

  

  const handleFileChange = (inputFile) => {
    if (!inputFile){
      setFile(null)
      setFilename(null)
    }
    else{
      setFile(inputFile);
      setFilename(inputFile.name);
    }
      
    
  }

  const handleCardChange = (card) => {
    setCard(card)
  }

  const handleAddMaster = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("card", card);
    try{
      const response = await fetch("http://127.0.0.1:8000/addMaster", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const result = await response.json();
        alert(result.message);  // Show error message
        return;
      }
      const result = await response.json();
      alert(result.message);
    } 
    catch (error){
      alert("Error adding to master")
    }
  }

    return (
        <div>
            <h1>React + FastAPI</h1>
            <p>Message from backend: {message}</p>
            <Group align="flex-end">
              <FileInput 
                accept=".csv"
                label="Select CSV"
                description="Choose a .csv file to add to master.csv"
                onChange={handleFileChange}
                style={{ minWidth: 250 }}
              />

              <Select
                label="Card Company"
                description = "Choose which company the csv is from"
                data={['TD', 'Rogers', 'Amex', 'Tangerine']}
                onChange={handleCardChange}
              />

              <Button onClick={handleAddMaster} disabled={!file || !card}>
                Add to master
              </Button>
            </Group>
            <MasterTable/>
        </div>
      );
};

export default App;
