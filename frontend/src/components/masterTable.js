import React from "react"; 
import { Table, Button, Stack, Group } from '@mantine/core'; 
const MasterTable = ({ tableData, onDataUpdate }) => {
    const handleAddRowToSheet = async (rowData, sheetName) => {
        const rowToUpdate = {
            hash: rowData.Hash,
            transactionDate: rowData["Transaction Date"],
            amount: rowData.Amount,
            description: rowData.Description,
            category: rowData.Category 
        };

        console.log(`Sending data for hash ${rowData.Hash} to sheet ${sheetName}`);

        try {
            const response = await fetch(`http://127.0.0.1:8000/updateCompletion/${sheetName}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(rowToUpdate), 
            });

            if (response.ok) {
                console.log(`Successfully sent data for hash ${rowData.Hash} to sheet ${sheetName}.`);
                onDataUpdate();
            } else {
                const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
                alert(`Error adding row (Hash: ${rowData.Hash}) to sheet ${sheetName}: ${response.status} ${response.statusText}. ${errorData.detail || ''}`);
                console.error("Backend error:", errorData);
            }
        } catch (error) {
            alert(`Network or other error adding row (Hash: ${rowData.Hash}) to sheet ${sheetName}: ${error}`);
            console.error("Fetch error:", error);
        }
    };


    // Map data to table rows, including the new action button
    const rows = tableData.map((item) => ( // Renamed loop variable for clarity
        <Table.Tr
            key={item.index ?? item.Hash} 
        >
            <Table.Td>{item["Transaction Date"]}</Table.Td>
            <Table.Td>{item.Amount}</Table.Td>
            <Table.Td>{item.Description}</Table.Td>
            <Table.Td>{item.Category}</Table.Td>

            <Table.Td>
              <Group gap = "xs">
                <Button
                      size="xs" 
                      onClick={() => handleAddRowToSheet(item, 'Shahzan')} // Pass current row data and sheet name
                  >
                      Shahzan
                  </Button>
                  <Button
                      size="xs" 
                      onClick={() => handleAddRowToSheet(item, 'Baba')} // Pass current row data and sheet name
                  >
                      Baba
                  </Button>
                  <Button
                      size="xs" 
                      onClick={() => handleAddRowToSheet(item, 'Mama')} // Pass current row data and sheet name
                  >
                      Mama
                  </Button>
                  <Button
                      size="xs" 
                      onClick={() => handleAddRowToSheet(item, 'Ishal')} // Pass current row data and sheet name
                  >
                      Ishal
                  </Button>
              </Group>
                
            </Table.Td>

        </Table.Tr>
    ));

    return (
        <Stack m="md">
            <Table striped>
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th>Transaction Date</Table.Th>
                        <Table.Th>Amount</Table.Th>
                        <Table.Th>Description</Table.Th>
                        <Table.Th>Category</Table.Th>
                        <Table.Th>Actions</Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>{rows}</Table.Tbody>
            </Table>
        </Stack>
    )

};
export default MasterTable;