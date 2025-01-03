import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Typography } from '@mui/material';
import { toast } from 'react-toastify';

const UploadFilesDialog = React.forwardRef((props, ref) => {
  const [open, setOpen] = React.useState(false);

  const [file, setFile]         = React.useState<any>(null);
  const [dtd_file, setDtdFile]  = React.useState<any>(null);
  const [loading, setLoading]   = React.useState<boolean>(false);

  const handleFileChange = (event: any) => {
    const uploadedFile = event.target.files[0];
    setFile(uploadedFile);
  };

  const handleRemoveFile = () => {
    setFile(null);
  };

  const handleDtdFileChange = (event: any) => {
    const uploadedFile = event.target.files[0];
    setDtdFile(uploadedFile);
  };

  const handleDtdRemoveFile = () => {
    setDtdFile(null);
  };

  React.useImperativeHandle(ref, () => ({
    handleClickOpen() {
        setOpen(true)
    }
  }))

  const handleClose = () => {
    setOpen(false);
  }

  const handleSubmit = async () => {
    const formData = new FormData()

    formData.append("file", file)
    formData.append("dtd_file", dtd_file)

    setLoading(true)

    const promise = await fetch("/api/upload", {
      method: "POST",
      body: formData
    })

    if(!promise.ok){
      console.error(promise)
      toast.error(promise.statusText)
      return
    }

    setLoading(false)
  }

  return (
    <React.Fragment>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"Upload Files"}
        </DialogTitle>
        <DialogContent>
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 2,
                    p: 3,
                    border: "1px solid #ccc",
                    borderRadius: "8px",
                }}
            >
                <Typography variant="h6">Upload .csv file</Typography>
                {file ? (
                    <>
                        <Typography variant="body1">
                            Selected File: {file.name}
                        </Typography>
                        <Button variant="contained" color="error" onClick={handleRemoveFile}>
                            Remove File
                        </Button>
                    </>) : (
                    <Button
                        variant="contained"
                        component="label"
                    >
                        Select .csv file
                        <input
                            type="file"
                            hidden
                            onChange={handleFileChange}
                            accept=".csv"
                        />
                    </Button>
                )}
            </Box>
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 2,
                    p: 3,
                    border: "1px solid #ccc",
                    borderRadius: "8px",
                    marginTop: 1
                }}
            >
                <Typography variant="h6">Upload .dtd file</Typography>
                {dtd_file ? (
                    <>
                        <Typography variant="body1">
                            Selected File: {dtd_file.name}
                        </Typography>
                        <Button variant="contained" color="error" onClick={handleDtdRemoveFile}>
                            Remove File
                        </Button>
                    </>) : (
                    <Button
                        variant="contained"
                        component="label"
                    >
                        Select .dtd file
                        <input
                            type="file"
                            hidden
                            onChange={handleDtdFileChange}
                            accept=".dtd"
                        />
                    </Button>
                )}
            </Box>

            {loading === true &&
                <p>Loading request...</p>
            }
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button disabled={loading === true}  onClick={handleSubmit} autoFocus>
            Submit
          </Button >
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
})

export default UploadFilesDialog