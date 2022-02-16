import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"
import React, { useState } from "react"
import styled from "styled-components"

import { Carousel } from "@trendyol-js/react-carousel"

const StyledCarousel = styled(Carousel)`
  & > div > button {
    height: 100%;
    background: url(https://cdn.dsmcdn.com/web/production/slick-arrow.svg) 100% no-repeat;
    margin-left: 10px;
    margin-right: 10px;
    border: none;
  }

  & > div > button[data-direction=left] {
    transform: rotate(180deg);
  }

  & > div > button:focus {
    outline: none;
    box-shadow: none;
  }
`

export const ImageCarousel = () => {
  // Streamlit.setFrameHeight(200)

  const renderData = useRenderData()

  const [isFocused, setIsFocused] = useState(false)

  const imgs = renderData.args["imgs"]
  const texts = renderData.args["texts"] || []
  const show = renderData.args["show_count"] || 4.5
  const slide = renderData.args["slide_count"] || 4

  const theme = renderData.theme
  const style = {}
  if (theme) {
    const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
    style.border = borderStyling
    style.outline = borderStyling
  }

  return (
    <StyledCarousel id="image_carousel" show={show} slide={slide} swiping={true}>
      {imgs.map((img, index) => {
        return (
          <div style={{ display: "flex", flexDirection: "column" }}>
            <img height="200px" width="200px" src={img} key={"img" + index} />
            {texts[index] || ""}
          </div>
        )
      })}
    </StyledCarousel>
  )
}

export default withStreamlitConnection(ImageCarousel)
