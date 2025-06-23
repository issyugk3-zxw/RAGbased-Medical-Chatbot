 const { app, BrowserWindow, ipcMain }=require('electron') 
const path = require('node:path')
const createWindow = () => {
  const win = new BrowserWindow({
    width: 1280,
    height: 972,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.ts')
    }
  })

  win.loadURL('http://localhost:3000')
}

ipcMain.on('send-value',( event,arg)=>{
  console.log( event , arg)
})
ipcMain.handle('getValue',( )=>{
  return "not implemented"
})


app.whenReady().then(() => {
  createWindow()
  
  // (MacOS)
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})