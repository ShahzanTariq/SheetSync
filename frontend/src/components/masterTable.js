import React, {useState, useRef} from "react"; 
import { Table, Button, Stack, Group, Tooltip, ActionIcon, Loader } from '@mantine/core'; 
import {IconTrash} from '@tabler/icons-react';
const MasterTable = ({ tableData, onDataUpdate }) => {
    const [loadingRows, setLoadingRows] = useState(new Set());
    const processingRef = useRef(new Set());

    const handleAddRowToSheet = async (rowData, sheetName) => {
        const hash = rowData.Hash;
        if (!hash || processingRef.current.has(hash)) {
            console.log(`Action for hash ${hash} already in progress (Ref Lock). Ignoring click.`);
            return;
        }

        processingRef.current.add(hash);
        setLoadingRows(prev => new Set(prev).add(hash));

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
        } finally {
            setLoadingRows(prev => {
                const next = new Set(prev);
                next.delete(hash);
                return next;
            });
        }
    };

    const handleIgnore = async (rowData) => {
        const hash = rowData.Hash

        if (!hash || processingRef.current.has(hash)) {
            console.log(`Action for hash ${hash} already in progress (Ref Lock). Ignoring click.`);
            return;
        }


        processingRef.current.add(hash);
        setLoadingRows(prev => new Set(prev).add(hash));

        try{
            const response = await fetch(`http://127.0.0.1:8000/updateIgnore/${hash}`, {
                method: "POST",
            });

            if (response.ok) {
                console.log(`Successfully ignored data for hash ${rowData.Hash}.`);
                onDataUpdate();
            } else {
                const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
                alert(`Error ignoring ${hash}`);
                console.error("Backend error:", errorData);
            }
        } catch (error){
            alert(`Error ignoring ${hash}`);
            console.error("Fetch error:", error);
        } finally {
            setLoadingRows(prev => {
                const next = new Set(prev);
                next.delete(hash);
                return next;
            });
        }
    }


    // Map data to table rows, including the new action button
    const rows = tableData.map((item) => { 
        const isLoading = loadingRows.has(item.Hash);
        return(
            <Table.Tr
            key={item.index ?? item.Hash} 
        >
            
            <Table.Td>{item["Transaction Date"]}</Table.Td>
            <Table.Td>{item.Amount}</Table.Td>
            <Table.Td>{item.Description}</Table.Td>
            <Table.Td>{item.Category}</Table.Td>

            <Table.Td>
              <Group gap = "xs">
                <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Shahzan')} disabled={isLoading}>Shahzan</Button>
                <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Baba')} disabled={isLoading}>Baba</Button>
                <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Mama')} disabled={isLoading}>Mama</Button>
                <Button size="xs" onClick={() => handleAddRowToSheet(item, 'Ishal')} disabled={isLoading}>Ishal</Button>
                <Tooltip label="Ignore Transaction" color="red" withArrow>
                    <ActionIcon variant="subtle" color="red" onClick={() => handleIgnore(item)} disabled={isLoading} title="Ignore">
                        {isLoading ? <Loader size={16} type="dots" color="red" /> : <IconTrash size={16} />}
                    </ActionIcon>
                </Tooltip>
              </Group>
                
            </Table.Td>

        </Table.Tr>
        )
        
    });

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