import React, { useEffect, useState } from "react";
import { FileInput, Select, Group, Button, Alert, List, Text, Title, Table, ScrollArea } from '@mantine/core'; 
import MasterTable from "./components/masterTable";
import { IconAlertCircle, IconCircleCheck, IconInfoCircle } from '@tabler/icons-react'; 


const App = () => {
  const [file, setFile] = useState(null);
  const [card, setCard] = useState("");
  const [tableData, setTableData] = useState([]);
  const [cardOptions, setCardOptions] = useState([]);
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);
  const [error, setError] = useState(null);
  const [submitStatus, setSubmitStatus] = useState({
      success: null,
      message: '',
      details: [],
      duplicates: [],
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

  const fetchCardOptions = () => {
    setIsLoadingOptions(true);
    setError(null);
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

  useEffect(() => {
    fetchTableData();
    fetchCardOptions();

    fetch(`${API_BASE_URL}/`)
      .then((res) => res.json())
      .catch((error) => console.error("Error fetching root message:", error));

  }, []);


  const handleDataUpdate = () => {
    console.log("MasterTable requested data update");
    fetchTableData();
  };

  const handleFileChange = (inputFile) => {
    setSubmitStatus({ success: null, message: '', details: [], duplicates: [] });
    setFile(inputFile);
  }

  const handleCardChange = (selectedCardValue) => {
      setSubmitStatus({ success: null, message: '', details: [], duplicates: [] });
      setCard(selectedCardValue);
  }

  const handleAddMaster = async () => {
    if (!file || !card) return;

    setSubmitStatus({ success: null, message: '', details: [], duplicates: [] });
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
              details: [`Response was not valid JSON.`],
              duplicates: []
          };
      }


      const success = response.ok; // Check if status code is 2xx
      setSubmitStatus({
          success: success,
          message: result.message || (success ? "Processing complete." : "Processing failed."),
          details: Array.isArray(result.details) ? result.details : [], // Ensure details is always an array
          duplicates: result.duplicate_rows
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
            details: [`Details: ${error.message}`],
            duplicates: []
        });
    } finally {
        setIsSubmitting(false);
    }
  };

    return (
        <div>
            <h1>Google Sheet Helper</h1>
            {error && (
                <Alert icon={<IconAlertCircle size="1rem" />} title="Error!" color="red" m="md" withCloseButton onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            <Group align="flex-end" m="md">
              <FileInput
                 accept=".csv"
                 label="Select CSV"
                 placeholder="Upload a CSV file"
                 description="Choose a .csv file to add to master.csv"
                 value={file} 
                 onChange={handleFileChange}
                 style={{ minWidth: 250 }}
                 clearable
              />
              <Select
                 label="Card Company"
                 placeholder="Select card type"
                 description = "Choose which company the csv is from"
                 data={cardOptions} 
                 value={card}
                 onChange={handleCardChange} 
                 disabled={isLoadingOptions}
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

             {submitStatus.message && (
                <Alert
                    icon={
                        submitStatus.success === true ? <IconCircleCheck size="1rem" /> :
                        submitStatus.success === false ? <IconAlertCircle size="1rem" /> :
                        <IconInfoCircle size="1rem" /> // Use info icon if status is null (e.g., during initial state)
                    }
                    title={submitStatus.success ? "Success!" : "Processing Issue"}
                    color={submitStatus.success ? "green" : "orange"} // Green for success, Orange for issues/errors
                    m="md"
                    withCloseButton onClose={() => setSubmitStatus({ success: null, message: '', details: [], duplicates: [] })} // Allow dismissal
                >
                    <Text fw={500} mb="xs">{submitStatus.message}</Text> 
                    {/* Display detailed messages if they exist */}
                    {submitStatus.details && submitStatus.details.length > 0 && (
                        <List size="sm" spacing="xs" mt="sm">
                            {submitStatus.details.map((detail, index) => (
                                <List.Item key={index}>{detail}</List.Item>
                            ))}
                        </List> 
                    )}
                    {submitStatus.duplicates && submitStatus.duplicates.length > 0 && (
                    <>
                        <Title order={6} mb="xs" mt="md">Skipped Duplicate Rows:</Title>
                        <ScrollArea style={{ height: 150, border: '1px solid var(--mantine-color-gray-3)', borderRadius: 'var(--mantine-radius-sm)' }}> {/* Adjust height/style */}
                            <Table fontSize="xs" striped withTableBorder withColumnBorders>
                                <Table.Thead>
                                    <Table.Tr>
                                        {Object.keys(submitStatus.duplicates[0] || {}).map(key => (
                                            <Table.Th key={key}>{key}</Table.Th>
                                        ))}
                                    </Table.Tr>
                                </Table.Thead>
                                <Table.Tbody>
                                    {submitStatus.duplicates.map((row, index) => (
                                        <Table.Tr key={row.Hash || index}>
                                            {Object.entries(row).map(([key, value]) => (
                                                <Table.Td key={key}>{String(value)}</Table.Td>
                                            ))}
                                        </Table.Tr>
                                    ))}
                                </Table.Tbody>
                            </Table>
                        </ScrollArea>
                    </>
                )}
                </Alert>
             )}

            <MasterTable tableData={tableData} onDataUpdate={handleDataUpdate} />

        </div>
      );
};

export default App;