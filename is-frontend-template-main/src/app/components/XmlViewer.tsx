"use client"

import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Tab, Tabs, TextField } from '@mui/material';
import { Search } from '@mui/icons-material';
import { toast, ToastContainer } from 'react-toastify';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function CustomTabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;
  
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        {...other}
      >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
      </div>
    );
  }

function a11yProps(index: number) {
    return {
      id: `simple-tab-${index}`,
      'aria-controls': `simple-tabpanel-${index}`,
    };
}

const XmlViewerDialog = React.forwardRef((_, ref) => {
  const [open, setOpen]     = React.useState(false)
  const [value, setValue]   = React.useState(0);
  const [xml_filtered_by_city, setXmlFilteredByCity] = React.useState<string>("<cities></cities>");

  const [searchByCityForm, setSearchByCityForm]  = React.useState({
    city: ''
  })

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  React.useImperativeHandle(ref, () => ({
    handleClickOpen() {
        setOpen(true)
    }
  }))

  const handleClose = () => {
    setOpen(false);
  }

  const handleSubmit = async (e: any) => {
    e.preventDefault()

    const params = {
        city: searchByCityForm.city
    }

    const response = await fetch("/api/xml/filter-by-city", {
        method: "POST",
        body: JSON.stringify(params),
        headers: {
            'content-type': 'application/json'
        }
    })

    if(!response.ok){
        toast.error(response.statusText)
        return
    }

    const text      = await response.text()

    setXmlFilteredByCity(text)
  }

  return (
    <React.Fragment>
        <ToastContainer />

      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"XML Viewer"}
        </DialogTitle>

        <DialogContent>

            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                    <Tab label="Search by city" {...a11yProps(0)} />
                </Tabs>
            </Box>
            
            <CustomTabPanel value={value} index={0}>
                <Box className='px-0' component="form" onSubmit={handleSubmit}>
                    <TextField
                        label="Search by city name"
                        fullWidth
                        margin="normal"
                        value={searchByCityForm.city}
                        onChange={(e: any) => {setSearchByCityForm({...searchByCityForm, city: e.target.value})}}
                    />

                    <Button fullWidth type="submit" variant="contained" startIcon={<Search />} />
                </Box>

                <pre className='my-4 mx-0' style={{ fontFamily: "monospace" }}>
                    <code>{xml_filtered_by_city}</code>
                </pre>
            </CustomTabPanel>
            
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
})

export default XmlViewerDialog