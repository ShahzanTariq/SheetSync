// App.js
import React, { useEffect, useState } from "react";
import { FileInput, Select, Group, Button, Alert, List, Text } from '@mantine/core'; 
import MasterTable from "./components/masterTable";
import { IconAlertCircle, IconCircleCheck, IconInfoCircle } from '@tabler/icons-react'; 


const App = () => {
  const [message, setMessage] = useState(""); // Backend root message
  const [file, setFile] = useState(null);
  const [card, setCard] = useState("");
  const [tableData, setTableData] = useState([]);
  const [cardOptions, setCardOptions] = useState([]);
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);
  const [error, setError] = useState(null); // General errors
  const [submitStatus, setSubmitStatus] = useState({ // Consolidate submit feedback
      success: null, // boolean or null
      message: '',   // Main message from backend
      details: [],   // Detailed messages list from backend
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const API_BASE_URL = "http://127.0.0.1:8000";

  const fetchTableData = () => {
    setError(null);
    fetch(`${API_BASE_URL}/getMaster`)
      .then(res => {
          if (!res.ok) { throw new Error(`HTTP error! status: ${res.status}`); }
          return res.json();
       })
      .then(data => setTableData(data))
      .catch(error => {
          console.error("Error fetching master data:", error);
          setError("Failed to load master data. Is the backend running?");
          setTableData([]); // Clear table on error
      });
  };

  // Fetch Card Options for dropdown
  const fetchCardOptions = () => {
    setIsLoadingOptions(true);
    setError(null); // Clear general errors related to options loading
    fetch(`${API_BASE_URL}/getCardOptions`)
      .then(res => {
        if (!res.ok) { throw new Error(`HTTP error! status: ${res.status}`); }
        return res.json();
      })
      .then(data => {
        setCardOptions(data || []);
        setIsLoadingOptions(false);
      })
      .catch(error => {
        console.error("Error fetching card options:", error);
        setError("Failed to load card options. Check backend and config.json.");
        setCardOptions([]);
        setIsLoadingOptions(false);
      });
  };

  // Initial data loading
  useEffect(() => {
    fetchTableData();
    fetchCardOptions();

    fetch(`${API_BASE_URL}/`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error("Error fetching root message:", error));

  }, []);


  const handleDataUpdate = () => {
    console.log("MasterTable requested data update");
    fetchTableData();
  };

  const handleFileChange = (inputFile) => {
    setSubmitStatus({ success: null, message: '', details: [] }); // Clear previous status on new file select
    setFile(inputFile);
  }

  const handleCardChange = (selectedCardValue) => {
      setSubmitStatus({ success: null, message: '', details: [] }); // Clear previous status
      setCard(selectedCardValue);
  }

  const handleAddMaster = async () => {
    if (!file || !card) return;

    setSubmitStatus({ success: null, message: '', details: [] }); // Clear previous status
    setIsSubmitting(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("card", card);

    try {
      const response = await fetch(`${API_BASE_URL}/addMaster`, {
        method: "POST",
        body: formData,
      });

      // Attempt to parse JSON regardless of status code, backend might send details on error too
      let result = {};
      try {
          result = await response.json();
      } catch (jsonError) {
          // Handle cases where response is not JSON (e.g., server error page)
          console.error("Failed to parse JSON response:", jsonError);
          result = { // Create a default error structure
              message: `Server error (Status: ${response.status}). Check backend logs.`,
              details: [`Response was not valid JSON.`]
          };
      }


      const success = response.ok; // Check if status code is 2xx

      setSubmitStatus({
          success: success,
          message: result.message || (success ? "Processing complete." : "Processing failed."),
          details: Array.isArray(result.details) ? result.details : [] // Ensure details is always an array
      });

      if (success) {
        // Only update table and clear form on actual success where rows might have been added
        // Check details for "No new transactions" to avoid unnecessary refetch? Optional.
        if (!result.details?.some(d => d.includes("No new transactions found"))) {
             handleDataUpdate(); // Refetch master table
        }
        setFile(null); // Clear form on success
        setCard(null);
      }

    } catch (error) {
        console.error("Network error during submission:", error);
        setSubmitStatus({
            success: false,
            message: "Network error or backend unavailable.",
            details: [`Details: ${error.message}`]
        });
    } finally {
        setIsSubmitting(false);
    }
  };

    return (
        <div>
            <h1>Google Sheet Helper</h1>
            {/* Optional: Keep the initial backend message if desired */}
            {/* <p>Message from backend: {message}</p> */}

            {/* Display General Errors (like loading options/master data) */}
            {error && (
                <Alert icon={<IconAlertCircle size="1rem" />} title="Error!" color="red" m="md" withCloseButton onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* --- Input Group --- */}
            <Group align="flex-end" m="md">
              <FileInput
                // ... (props as before)
                 accept=".csv"
                 label="Select CSV"
                 placeholder="Upload a CSV file"
                 description="Choose a .csv file to add to master.csv"
                 value={file} // Control the component value
                 onChange={handleFileChange}
                 style={{ minWidth: 250 }}
                 clearable
              />
              <Select
                // ... (props as before)
                 label="Card Company"
                 placeholder="Select card type"
                 description = "Choose which company the csv is from"
                 data={cardOptions} // <<< BIND TO FETCHED OPTIONS
                 value={card} // Control the selected value
                 onChange={handleCardChange} // Use the handler
                 disabled={isLoadingOptions} // Disable while loading
                 searchable
                 nothingFoundMessage={isLoadingOptions ? "Loading..." : "No cards configured"}
                 clearable
              />
              <Button
                onClick={handleAddMaster}
                disabled={!file || !card || isSubmitting || isLoadingOptions}
                loading={isSubmitting}
              >
                Add to master
              </Button>
            </Group>

             {/* --- Display Submission Status/Details --- */}
             {submitStatus.message && ( // Only show if there's a message
                <Alert
                    icon={
                        submitStatus.success === true ? <IconCircleCheck size="1rem" /> :
                        submitStatus.success === false ? <IconAlertCircle size="1rem" /> :
                        <IconInfoCircle size="1rem" /> // Use info icon if status is null (e.g., during initial state)
                    }
                    title={submitStatus.success ? "Success!" : "Processing Issue"}
                    color={submitStatus.success ? "green" : "orange"} // Green for success, Orange for issues/errors
                    m="md"
                    withCloseButton onClose={() => setSubmitStatus({ success: null, message: '', details: [] })} // Allow dismissal
                >
                    <Text fw={500} mb="xs">{submitStatus.message}</Text> {/* Display main message */}
                    {/* Display detailed messages if they exist */}
                    {submitStatus.details && submitStatus.details.length > 0 && (
                        <List size="sm" spacing="xs" mt="sm">
                            {submitStatus.details.map((detail, index) => (
                                <List.Item key={index}>{detail}</List.Item>
                            ))}
                        </List>
                    )}
                </Alert>
             )}

            {/* --- Master Table --- */}
            <MasterTable tableData={tableData} onDataUpdate={handleDataUpdate} />

        </div>
      );
};

export default App;