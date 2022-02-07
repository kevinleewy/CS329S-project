import React from "react"
import ReactDOM from "react-dom"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks"
import ImageCarousel from "./ImageCarousel"
// import "./styles.css"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <ImageCarousel />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
