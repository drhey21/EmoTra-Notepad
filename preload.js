const { contextBridge } = require('electron');
const fs = require('fs');
const path = require('path');

const dataFilePath = path.join(__dirname, 'notes.json');
const draftFilePath = path.join(__dirname, 'draft.txt');

contextBridge.exposeInMainWorld('storageAPI', {
  saveDraft: (text) => {
    fs.writeFileSync(draftFilePath, text, 'utf8');
  },
  loadDraft: () => {
    if (fs.existsSync(draftFilePath)) {
      return fs.readFileSync(draftFilePath, 'utf8');
    }
    return '';
  },
  clearDraft: () => {
    if (fs.existsSync(draftFilePath)) {
      fs.unlinkSync(draftFilePath);
    }
  },
  loadNotes: () => {
    if (fs.existsSync(dataFilePath)) {
      try {
        return JSON.parse(fs.readFileSync(dataFilePath, 'utf8'));
      } catch (e) {
        return [];
      }
    }
    return [];
  },
  saveNotes: (notes) => {
    fs.writeFileSync(dataFilePath, JSON.stringify(notes, null, 2), 'utf8');
  }
});