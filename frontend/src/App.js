// App.js
import React, { useEffect, useState } from "react";
import { FileInput, Select, Group, Button, LoadingOverlay, Alert } from '@mantine/core'; // Added LoadingOverlay, Alert
import MasterTable from "./components/masterTable";
import { IconAlertCircle } from '@tabler/icons-react'; // For Alert icon

const App = () => {
  const [message, setMessage] = useState(""); // Backend root message
  const [file, setFile] = useState(null);
  const [card, setCard] = useState("");
  const [tableData, setTableData] = useState([]);
  const [cardTypes, setCardTypes] = useState([]); // State for dropdown options
  const [loading, setLoading] = useState(false); // Loading state for uploads/fetches
  const [fetchError, setFetchError] = useState(null); // Error fetching table data
  const [uploadError, setUploadError] = useState(null); // Error during upload
  const [uploadSuccess, setUploadSuccess] = useState(null); // Success message

  const API_BASE_URL = "http://127.0.0.1:8000"; // Centralize API URL

  // --- Fetch Master Table Data ---
  const fetchTableData = async () => {
    setLoading(true);
    setFetchError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/getMaster`);
      if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
          throw new Error(`Failed to fetch master data: ${response.status} ${errorData.detail || response.statusText}`);
      }
      const data = await response.json();
      // Add basic validation if needed (e.g., check if it's an array)
      if (Array.isArray(data)) {
         setTableData(data);
      } else {
          throw new Error("Received invalid data format for master table.");
      }
    } catch (error) {
      console.error("Error fetching master data:", error);
      setFetchError(error.message);
      setTableData([]); // Clear data on error
    } finally {
        setLoading(false);
    }
  };

  // --- Fetch Card Types for Dropdown ---
  useEffect(() => {
    const fetchCardTypes = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/getCardTypes`);
            if (!response.ok) {
                 throw new Error(`Failed to fetch card types: ${response.statusText}`);
            }
            const data = await response.json();
            setCardTypes(data); // Expecting [{ value: "TD", label: "TD Bank" }, ...]
        } catch (err) {
            console.error("Error fetching card types:", err);
            setFetchError("Could not load card types configuration from server.");
        }
    };
    fetchCardTypes();
  }, []); // Run once on mount

  // --- Fetch initial data ---
  useEffect(() => {
    fetchTableData(); // Fetch initial master data
     // Fetch root message (optional)
    fetch(`${API_BASE_URL}/`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.warn("Error fetching root message:", error));
  }, []); // Run once on mount


  // --- Callback for MasterTable ---
  const handleDataUpdate = () => {
    console.log("Data update requested from MasterTable.");
    fetchTableData(); // Refetch data
  };

  // --- File/Card Input Handlers ---
  const handleFileChange = (inputFile) => {
    setFile(inputFile);
    setUploadError(null); // Clear errors on new file
    setUploadSuccess(null);
  };

  const handleCardChange = (selectedCardValue) => {
    setCard(selectedCardValue); // Store the value ("TD", "Rogers")
    setUploadError(null); // Clear errors on new card selection
    setUploadSuccess(null);
  };

  // --- Upload Handler ---
  const handleAddMaster = async () => {
    if (!file || !card) {
        setUploadError("Please select both a file and a card type.");
        return;
    }
    setLoading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("card", card); // Send the key ("TD")

    try {
      const response = await fetch(`${API_BASE_URL}/addMaster`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json(); // Always try to parse JSON

      if (!response.ok) {
        // Use detail from backend error if available
        throw new Error(result.detail || `Upload failed with status ${response.status}`);
      }

      setUploadSuccess(result.message || "Upload successful!"); // Show success
      handleDataUpdate(); // Refresh table data
      setFile(null); // Clear file input after successful upload

    } catch (error) {
        console.error("Error adding to master:", error);
        setUploadError(`Upload failed: ${error.message}`);
    } finally {
        setLoading(false);
    }
  };

    return (
        <div style={{ padding: 'var(--mantine-spacing-md)' }}> {/* Add padding */}
            <LoadingOverlay visible={loading} overlayProps={{ radius: "sm", blur: 2 }} />
            <h1>Google Sheet Helper</h1>
            <p>Message from backend: {message}</p>

            {/* Error/Success Alerts */}
            {fetchError && (
                <Alert icon={<IconAlertCircle size="1rem" />} title="Data Fetch Error" color="red" withCloseButton onClose={() => setFetchError(null)} mb="md">
                    {fetchError}
                </Alert>
            )}
             {uploadError && (
                <Alert icon={<IconAlertCircle size="1rem" />} title="Upload Error" color="red" withCloseButton onClose={() => setUploadError(null)} mb="md">
                    {uploadError}
                </Alert>
            )}
            {uploadSuccess && (
                <Alert title="Upload Successful" color="green" withCloseButton onClose={() => setUploadSuccess(null)} mb="md">
                    {uploadSuccess}
                </Alert>
            )}


            {/* Upload Controls */}
            <Group align="flex-end" mb="md">
              <FileInput
                label="Select CSV"
                placeholder="Click to select file"
                description="Choose a .csv file"
                value={file} // Controlled component
                onChange={handleFileChange}
                accept=".csv, text/csv"
                clearable // Allow clearing the file
                style={{ minWidth: 250 }}
                disabled={loading}
              />

              <Select
                label="Card Company"
                placeholder="Choose card"
                description = "Select the source card"
                data={cardTypes} // Use fetched card types
                value={card}
                onChange={handleCardChange} // Passes the value ("TD")
                searchable
                clearable
                nothingFoundMessage={cardTypes.length > 0 ? "No match" : "Loading..."}
                disabled={loading || cardTypes.length === 0}
              />

              <Button onClick={handleAddMaster} disabled={!file || !card || loading}>
                Add to master
              </Button>
            </Group>

            {/* Master Table */}
            <MasterTable tableData={tableData} onDataUpdate={handleDataUpdate} />

        </div>
      );
};

export default App;