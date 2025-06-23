const { contextBridge, ipcRender} = require('electron')

contextBridge.exposeInMainWorld('eAPI', {
  sendValue:(value) =>{
    ipcRender.send('send-value',value)

  },
  getValue:() =>{
    ipcRender.invoke('getValue')
  }
  
})