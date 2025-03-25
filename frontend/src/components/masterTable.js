import React, { useState } from "react";
import { Table, Checkbox, Button, Stack } from '@mantine/core';

const MasterTable = ({ tableData, onDataUpdate }) => {
    const [selectedRows, setSelectedRows] = useState([]);


    const handleShahzan = async () => {
      try{
        const response = await fetch("http://127.0.0.1:8000/updateCompletion", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ hash: selectedRows }),
        });
        if (response.ok){
          onDataUpdate();
          setSelectedRows([]);
        }
      } 
      catch (error){
        alert("Error updating completion")
      }
    }
    
    
    const rows  = tableData.map((tableData) => (
        <Table.Tr
            key={tableData.index}
            bg={selectedRows.includes(tableData.Hash) ? 'var(--mantine-color-blue-light)' : undefined}
        >
            <Table.Td>
                <Checkbox
                    aria-label="Select row"
                    checked={selectedRows.includes(tableData.Hash)}
                    onChange={(event) =>
                        setSelectedRows(
                          event.currentTarget.checked
                            ? [...selectedRows, tableData.Hash]
                            : selectedRows.filter((Hash) => Hash !== tableData.Hash)
                        )
                    }
                />
            </Table.Td>
            <Table.Td>{tableData["Transaction Date"]}</Table.Td>
            <Table.Td>{tableData.Amount}</Table.Td>
            <Table.Td>{tableData.Description}</Table.Td>
            <Table.Td>{tableData.Category}</Table.Td>

    </Table.Tr>
    ));

    return(
      <Stack>
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th />
              <Table.Th>Transaction Date</Table.Th>
              <Table.Th>Amount</Table.Th>
              <Table.Th>Description</Table.Th>
              <Table.Th>Category</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{rows}</Table.Tbody>
        </Table>
        <Button onClick={handleShahzan} disabled={!selectedRows}>
          Shahzan Sheet
        </Button>
      </Stack>
    )

};
export default MasterTable
    






