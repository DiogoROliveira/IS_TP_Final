import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Typography } from '@mui/material';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'react-toastify';

const UploadFilesDialog = React.forwardRef(
  ({ onUploadStatusChange }: { onUploadStatusChange: (status: any) => void }, ref) => {
    const [open, setOpen] = React.useState(false);

    const [file, setFile] = React.useState<any>(null);
    const [dtd_file, setDtdFile] = React.useState<any>(null);
    const [uploadStatus, setUploadStatus] = React.useState({
      loading: false,
      progress: 'idle',
      message: ''
    });

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
        setOpen(true);
      }
    }));

    const handleClose = () => {
      if (!uploadStatus.loading) {
        setOpen(false);
        setUploadStatus({ loading: false, progress: 'idle', message: '' });
      }
    };

    const handleSubmit = async () => {
      const formData = new FormData();

      formData.append('file', file);
      formData.append('dtd_file', dtd_file);

      const newStatus = { loading: true, progress: 'uploading', message: 'Uploading files...' };
      setUploadStatus(newStatus);
      onUploadStatusChange(newStatus);

      const promise = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (!promise.ok) {
        const errorStatus = {
          loading: false,
          progress: 'error',
          message: `Error: ${promise.statusText}`
        };
        setUploadStatus(errorStatus);
        onUploadStatusChange(errorStatus);
        toast.error(promise.statusText);
        return;
      }

      const successStatus = {
        loading: false,
        progress: 'success',
        message: 'Files uploaded and processed successfully!'
      };
      setUploadStatus(successStatus);
      onUploadStatusChange(successStatus);

      setTimeout(() => {
        handleClose();
        setFile(null);
        setDtdFile(null);
      }, 2000);
    };

    return (
      <React.Fragment>
        <Dialog
          open={open}
          onClose={handleClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">{'Upload Files'}</DialogTitle>
          <DialogContent>
            {/* File upload sections */}
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, p: 3 }}>
              <Typography variant="h6">Upload .csv file</Typography>
              {file ? (
                <>
                  <Typography variant="body1">Selected File: {file.name}</Typography>
                  <Button variant="contained" color="error" onClick={handleRemoveFile}>
                    Remove File
                  </Button>
                </>
              ) : (
                <Button variant="contained" component="label">
                  Select .csv file
                  <input type="file" hidden onChange={handleFileChange} accept=".csv" />
                </Button>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button disabled={uploadStatus.loading || !file} onClick={handleSubmit} autoFocus>
              Submit
            </Button>
          </DialogActions>
        </Dialog>
      </React.Fragment>
    );
  }
);

export default UploadFilesDialog;
