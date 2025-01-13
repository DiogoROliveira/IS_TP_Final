"use client"

import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Tab, Tabs, TextField, Checkbox, FormControlLabel } from '@mui/material';
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

function formatXml(xml: string): string {
  
  xml = xml.replace(/>\s+</g, '><').trim();
  
  
  const PADDING = ' '.repeat(2); 
  const reg = /(>)(<)(\/*)/g;
  let formatted = xml.replace(reg, '$1\r\n$2$3');
  let pad = 0;
  
  
  return formatted.split('\r\n').map(line => {    
      if (line.match(/<\//)) {
          pad -= 1;
      }
      
      const indent = PADDING.repeat(Math.max(0, pad));
      line = indent + line;
      
      if (line.match(/<[^/!].*?>/) && !line.match(/\/>/)) {
          pad += 1;
      }
      
      return line;
  }).join('\n');
}

function a11yProps(index: number) {
    return {
      id: `simple-tab-${index}`,
      'aria-controls': `simple-tabpanel-${index}`,
    };
}

const XmlViewerDialog = React.forwardRef((_, ref) => {
  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState(0);
  const [xmlFilteredByCity, setXmlFilteredByCity] = React.useState<string>("");

  const [searchByCityForm, setSearchByCityForm] = React.useState({
    city: ''
  });

  const [orderByForm, setOrderByForm] = React.useState({
    expression: '',
    ascending: true
  });

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
    setXmlFilteredByCity('');
  };

  React.useImperativeHandle(ref, () => ({
    handleClickOpen() {
        setOpen(true);
        setXmlFilteredByCity('');
    }
  }));

  const handleClose = () => {
    setOpen(false);
    setXmlFilteredByCity('');
    setValue(0);
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();

    const params = {
        city: searchByCityForm.city
    };

    try {
        const response = await fetch("/api/xml/filter-by-city", {
            method: "POST",
            body: JSON.stringify(params),
            headers: {
                'content-type': 'application/json'
            }
        });

        if (!response.ok) {
            toast.error(response.statusText);
            return;
        }

        const text = await response.text();
        const formattedXml = formatXml(text);
        setXmlFilteredByCity(formattedXml);
    } catch (error) {
        toast.error('An error occurred while processing the XML');
    }
  };

  const handleOrderBy = async (e: any) => {
    e.preventDefault();

    const params = {
        expression: orderByForm.expression,
        ascending: orderByForm.ascending
    };

    try {
        const response = await fetch("/api/xml/order-by", {
            method: "POST",
            body: JSON.stringify(params),
            headers: {
                'content-type': 'application/json'
            }
        });

        if (!response.ok) {
            toast.error(response.statusText);
            return;
        }

        const text = await response.text();
        const formattedXml = formatXml(text);
        setXmlFilteredByCity(formattedXml);
    } catch (error) {
        toast.error('An error occurred while processing the XML');
    }
};

return (
  <React.Fragment>
      <ToastContainer />
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        maxWidth="md"
        fullWidth
      >
        <DialogTitle id="alert-dialog-title">
          {"XML Viewer"}
        </DialogTitle>

        <DialogContent>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                    <Tab label="Search by city" {...a11yProps(0)} />
                    <Tab label="Group-by" {...a11yProps(1)} />
                    <Tab label="Order-by" {...a11yProps(2)} />
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

                {xmlFilteredByCity && (
                  <pre className='my-4 mx-0' style={{ 
                      fontFamily: "monospace", 
                      whiteSpace: "pre-wrap",
                      backgroundColor: '#f5f5f5',
                      padding: '1rem',
                      borderRadius: '4px'
                  }}>
                      <code>{xmlFilteredByCity}</code>
                  </pre>
                )}
            </CustomTabPanel>

            <CustomTabPanel value={value} index={2}>
              <Box className='px-0' component="form" onSubmit={handleOrderBy}>
                  <TextField
                      label="Expression"
                      fullWidth
                      margin="normal"
                      value={orderByForm.expression}
                      onChange={(e: any) => {setOrderByForm({...orderByForm, expression: e.target.value})}}
                  />

                  <FormControlLabel
                      control={
                          <Checkbox
                              checked={orderByForm.ascending}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {setOrderByForm({...orderByForm, ascending: e.target.checked})}}
                          />
                      }
                      label="Ascending"
                  />

                  <Button fullWidth type="submit" variant="contained" startIcon={<Search />} />
              </Box>
              {xmlFilteredByCity && (
                <pre className='my-4 mx-0' style={{ 
                    fontFamily: "monospace", 
                    whiteSpace: "pre-wrap",
                    backgroundColor: '#f5f5f5',
                    padding: '1rem',
                    borderRadius: '4px'
                }}>
                    <code>{xmlFilteredByCity}</code>
                </pre>
              )}
            </CustomTabPanel>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
        </DialogActions>
      </Dialog>
  </React.Fragment>
);
});

export default XmlViewerDialog;