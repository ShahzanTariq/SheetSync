// components/masterTable.js
import React from "react";
import { Table, Button, Group } from '@mantine/core'; // Removed Stack unless needed elsewhere

const MasterTable = ({ tableData = [], onDataUpdate }) => { // Added default for tableData

    // --- IMPORTANT: Make sure ItemDetail keys match backend Pydantic model ---
    const handleAddRowToSheet = async (rowData, sheetNameKey) => { // Use sheetNameKey
        // Ensure all required fields exist in rowData
        if (!rowData || !rowData.Hash || !rowData["Transaction Date"] || rowData.Amount == null || !rowData.Description) {
             console.error("Row data is missing required fields:", rowData);
             alert("Cannot process row: missing required data.");
             return;
        }

        const rowPayload = {
            hash: String(rowData.Hash), // Ensure hash is string
            transactionDate: rowData["Transaction Date"],
            amount: parseFloat(rowData.Amount), // Ensure amount is number
            description: rowData.Description,
            // Ensure category matches backend model (send null if optional and not present)
            category: rowData.Category || null
        };

        console.log(`Sending data for hash ${rowPayload.hash} to sheet key ${sheetNameKey}`);
        console.log("Payload:", rowPayload); // Log the payload being sent

        try {
            const response = await fetch(`http://127.0.0.1:8000/updateCompletion/${sheetNameKey}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                // --- Send the single object directly ---
                body: JSON.stringify(rowPayload),
            });

            // Rest of the fetch logic (check response.ok, handle errors)
            if (response.ok) {
                console.log(`Successfully processed row (Hash: ${rowPayload.hash}) for sheet key ${sheetNameKey}.`);
                onDataUpdate(); // Refresh the master table data
            } else {
                const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
                 // Check for specific FastAPI validation error structure
                let errorMsg = errorData.detail || `Request failed: ${response.status}`;
                if (typeof errorData.detail === 'object' && errorData.detail !== null) {
                     // Handle FastAPI validation errors (often lists of dicts)
                     errorMsg = errorData.detail.map(err => `${err.loc ? err.loc.join('.') : 'error'}: ${err.msg}`).join('; ');
                 } else if (Array.isArray(errorData.detail)) {
                     errorMsg = errorData.detail.join(', ');
                 }

                alert(`Error processing row (Hash: ${rowPayload.hash}) for sheet ${sheetNameKey}: ${errorMsg}`);
                console.error("Backend error:", errorData);
            }

        } catch (error) {
            alert(`Network error processing row (Hash: ${rowPayload.hash}) for sheet ${sheetNameKey}: ${error.message}`);
            console.error("Fetch error:", error);
        }
    };


    // Map data to table rows
    const rows = tableData.map((item) => (
        <Table.Tr key={item.index ?? item.Hash}>
            <Table.Td>{item["Transaction Date"]}</Table.Td>
            <Table.Td>{item.Amount?.toFixed(2)}</Table.Td> {/* Format amount */}
            <Table.Td>{item.Description}</Table.Td>
            <Table.Td>{item.Category || '-'}</Table.Td> {/* Show dash if no category */}
            <Table.Td>
              <Group gap="xs">
                 {/* Generate buttons dynamically maybe? Or keep hardcoded */}
                 <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Shahzan')}>Shahzan</Button>
                 <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Baba')}>Baba</Button>
                 <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Mama')}>Mama</Button>
                 <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Ishal')}>Ishal</Button>
              </Group>
            </Table.Td>
        </Table.Tr>
    ));

    return (
        // Removed outer Stack, add padding/margin to App.js div or here if needed
        <Table>
            <Table.Thead>
                <Table.Tr>
                    <Table.Th>Transaction Date</Table.Th>
                    <Table.Th>Amount</Table.Th>
                    <Table.Th>Description</Table.Th>
                    <Table.Th>Category</Table.Th>
                    <Table.Th>Actions</Table.Th>
                </Table.Tr>
            </Table.Thead>
            {/* Show message if no data */}
            <Table.Tbody>{rows.length > 0 ? rows : <Table.Tr><Table.Td colSpan={5} align="center">No incomplete transactions found.</Table.Td></Table.Tr>}</Table.Tbody>
        </Table>
    )
};

export default MasterTable;