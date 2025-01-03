"use client"

import React, { useRef } from 'react';
import { List, ListItem, ListItemText, Box, ListSubheader, ListItemButton, TextField, Button } from '@mui/material';
import UploadFilesDialog from './UploadFilesDialog';
import XmlViewerDialog from './XmlViewer';
import { Search } from '@mui/icons-material';
import { redirect } from 'next/navigation';

const Sidebar = ({ searchValue } : { searchValue: string }) => {
    const uploadFilesDialogRef  = useRef<any>(null)
    const xmlViewerDialog       = useRef<any>(null)

    const [searchByCityForm, setSearchByCityForm] = React.useState({
        city: searchValue
    })

    const handleOpenUploadFilesDialog = () => {
        if(!uploadFilesDialogRef || !uploadFilesDialogRef.current) return

        uploadFilesDialogRef.current.handleClickOpen() // Call child's increment function
    }

    const handleXmlViewerDialog = () => {
        if(!xmlViewerDialog || !xmlViewerDialog.current) return

        xmlViewerDialog.current.handleClickOpen() // Call child's increment function
    }

    const handleSubmit = async (e: any) => {
        e.preventDefault()
    
        redirect(`/?search=${searchByCityForm.city}`)
      }

    return (
        <>
            <UploadFilesDialog ref={uploadFilesDialogRef} />
            <XmlViewerDialog ref={xmlViewerDialog} />
        
            <List
                sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
                component="nav"
                aria-labelledby="nested-list-subheader"
                subheader={
                    <ListSubheader className="text-black font-bold border-b-2" component="div" id="nested-list-subheader">
                        <p className='text-gray-700 font-bold text-xl my-4'>IS - FINAL</p>
                    </ListSubheader>
                }>
                <ListItem>
                    <Box className='' component="form" onSubmit={handleSubmit}>
                        <TextField
                            label="Search by city name"
                            fullWidth
                            margin="normal"
                            value={searchByCityForm.city}
                            onChange={(e: any) => {setSearchByCityForm({...searchByCityForm, city: e.target.value})}}
                        />

                        <Button fullWidth type="submit" variant="contained" startIcon={<Search />} />
                    </Box>
                </ListItem>
                <ListItemButton onClick={handleOpenUploadFilesDialog}>
                    <ListItemText className="text-gray-600" primary="Upload File" />
                </ListItemButton>
                <ListItemButton onClick={handleXmlViewerDialog}>
                    <ListItemText className="text-gray-600" primary="XMLs" />
                </ListItemButton>
            </List>
        </>
    )
};

export default Sidebar;
