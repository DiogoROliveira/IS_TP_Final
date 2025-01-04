"use client";

import React, { useRef, useState } from "react";
import {
  List,
  ListItem,
  ListItemText,
  Box,
  ListSubheader,
  ListItemButton,
  TextField,
  Button,
  CircularProgress,
} from "@mui/material";
import UploadFilesDialog from "./UploadFilesDialog";
import XmlViewerDialog from "./XmlViewer";
import { Search } from "@mui/icons-material";
import { redirect } from "next/navigation";
import { toast } from "react-toastify";

const Sidebar = ({ searchValue }: { searchValue: string }) => {
  const uploadFilesDialogRef = useRef<any>(null);
  const xmlViewerDialog = useRef<any>(null);
  const [status, setStatus] = useState({
    loading: false,
    progress: "idle",
    message: "",
  });

  const [searchByCityForm, setSearchByCityForm] = React.useState({
    city: searchValue,
  });

  const handleStatusChange = (newStatus: any) => {
    setStatus(newStatus);
    if (newStatus.progress === "success") {
      toast.success(newStatus.message);
    } else if (newStatus.progress === "error") {
      toast.error(newStatus.message);
    }
  };

  const handleOpenUploadFilesDialog = () => {
    if (!uploadFilesDialogRef || !uploadFilesDialogRef.current) return;
    uploadFilesDialogRef.current.handleClickOpen();
  };

  const handleXmlViewerDialog = () => {
    if (!xmlViewerDialog || !xmlViewerDialog.current) return;
    xmlViewerDialog.current.handleClickOpen();
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    redirect(`/?search=${searchByCityForm.city}`);
  };

  return (
    <>
      <UploadFilesDialog
        ref={uploadFilesDialogRef}
        onUploadStatusChange={handleStatusChange}
      />
      <XmlViewerDialog ref={xmlViewerDialog} />

      <List
        sx={{ width: "100%", maxWidth: 360, bgcolor: "background.paper" }}
        component="nav"
        aria-labelledby="nested-list-subheader"
        subheader={
          <ListSubheader
            className="text-black font-bold border-b-2"
            component="div"
            id="nested-list-subheader"
          >
            <p className="text-gray-700 font-bold text-xl my-4">IS - FINAL</p>
          </ListSubheader>
        }
      >
        <ListItem>
          <Box className="" component="form" onSubmit={handleSubmit}>
            <TextField
              label="Search by city name"
              fullWidth
              margin="normal"
              value={searchByCityForm.city}
              onChange={(e: any) =>
                setSearchByCityForm({ ...searchByCityForm, city: e.target.value })
              }
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              startIcon={<Search />}
            />
          </Box>
        </ListItem>
        <ListItemButton
          onClick={handleOpenUploadFilesDialog}
          disabled={status.loading}
        >
          <ListItemText className="text-gray-600" primary="Upload File" />
          {status.loading && <CircularProgress size={20} />}
        </ListItemButton>
        <ListItemButton onClick={handleXmlViewerDialog}>
          <ListItemText className="text-gray-600" primary="XMLs" />
        </ListItemButton>
      </List>

      {/* Feedback visual para o upload */}
      {status.progress !== "idle" && (
        <Box
          sx={{
            p: 2,
            mt: 2,
            border: "1px solid #ccc",
            borderRadius: "8px",
            backgroundColor: "#f9f9f9",
          }}
        >
          <p>
            <strong>Status:</strong> {status.message}
          </p>
        </Box>
      )}
    </>
  );
};

export default Sidebar;

