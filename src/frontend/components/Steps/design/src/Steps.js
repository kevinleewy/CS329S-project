import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"
import React, { useState } from "react"
import styled from "styled-components"

import { Steps } from "antd"
import { FileImageOutlined, ExperimentOutlined, SkinOutlined, FireOutlined } from "@ant-design/icons"

import "antd/dist/antd.css"

const { Step } = Steps

const getStyledSteps = (textColor, primaryColor) => styled(Steps)`
  color: #bfbfbf !important;

  .ant-steps-item-title {
    color: #bfbfbf !important;
  }
  .ant-steps-item-custom > .ant-steps-item-container > .ant-steps-item-icon > .ant-steps-icon {
    color: #bfbfbf !important;
    top: -5px !important;
  }

  .ant-steps-item-wait > .ant-steps-item-container > .ant-steps-item-content > .ant-steps-item-title:after {
    background-color: #bfbfbf !important;
  }

  .ant-steps-item-process > .ant-steps-item-container > .ant-steps-item-content > .ant-steps-item-title,
  .ant-steps-item-process > .ant-steps-item-container > .ant-steps-item-icon > .ant-steps-icon {
    color: ${primaryColor} !important;
  }
  .ant-steps-item-process > .ant-steps-item-container > .ant-steps-item-content > .ant-steps-item-title:after {
    background-color: #bfbfbf !important;
  }

  .ant-steps-item-finish > .ant-steps-item-container > .ant-steps-item-content > .ant-steps-item-title,
  .ant-steps-item-finish > .ant-steps-item-container > .ant-steps-item-icon > .ant-steps-icon {
    color: ${textColor} !important;
  }
  .ant-steps-item-finish > .ant-steps-item-container > .ant-steps-item-content > .ant-steps-item-title:after {
    background-color: ${textColor} !important;
  }
`

export const HeaderSteps = () => {
  // Streamlit.setFrameHeight(100)

  const renderData = useRenderData()

  const [isFocused, setIsFocused] = useState(false)

  const choose_status = renderData.args["choose_status"]
  const find_status = renderData.args["find_status"]
  const explore_status = renderData.args["explore_status"]
  const rate_status = renderData.args["rate_status"]

  const theme = renderData.theme
  console.log(theme)
  const style = {}
  if (theme) {
    const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
    style.border = borderStyling
    style.outline = borderStyling
  }

  const StyledSteps = getStyledSteps(theme.textColor, theme.primaryColor)
  return (
    <StyledSteps>
      <Step status={choose_status} title="Choose Images" icon={<FileImageOutlined />} />
      <Step status={find_status} title="Run Model" icon={<ExperimentOutlined />} />
      <Step status={explore_status} title="Explore Fits" icon={<SkinOutlined />} />
      <Step status={rate_status} title="Rate Fits" icon={<FireOutlined />} />
    </StyledSteps>
  )
}

export default withStreamlitConnection(HeaderSteps)
