import React, { useEffect, useState } from "react";
import { Table, Checkbox } from '@mantine/core';

const MasterTable = () => {
    const [tableData, setTableData] = useState([]);
    const [selectedRows, setSelectedRows] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/getMaster")
          .then((res) => {return res.json();})
          .then((data) => setTableData(data))
          .catch((error) => console.error("Error fetching:", error));
    }, [])

    
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

    )

};
export default MasterTable
    






