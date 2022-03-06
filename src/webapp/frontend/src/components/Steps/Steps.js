import React, { useState } from 'react';
import styled from "styled-components"
import { Steps, Button, message } from 'antd';

import "antd/dist/antd.css"

const { Step } = Steps;

const getStyledSteps = (textColor, primaryColor) => styled(Steps)`
  color: #bfbfbf !important;

  .ant-steps-item-title {
    color: #bfbfbf !important;
  }
  .ant-steps-item-custom > .ant-steps-item-container > .ant-steps-item-icon > .ant-steps-icon {
    color: #bfbfbf !important;
    // top: -5px !important;
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

const HeaderSteps = ({steps, current, setCurrent}) => {
  const next = () => {
    setCurrent(current + (steps[current].next_addition || 1));
  };

  const prev = () => {
    setCurrent(current + (steps[current].prev_addition || -1));
  };

  const StyledSteps = getStyledSteps("#1a90ffd9", "black")
  return (
    <>
      <StyledSteps current={current}>
        {steps.map(item => (
          <Step key={item.title} title={item.title} icon={item.icon} />
        ))}
      </StyledSteps>
    </>
  )

  return (
    <>
      <StyledSteps current={current}>
        {steps.map(item => (
          <Step key={item.title} title={item.title} icon={item.icon} />
        ))}
      </StyledSteps>
      <div className="steps-content">{steps[current].content}</div>
      <div className="steps-action">
        {current < steps.length - 1 && steps[current].next_button && (
          <Button type="primary" onClick={steps[current].next_on_click || (() => next())}>
            {steps[current].next_button}
          </Button>
        )}
        {current === steps.length - 1 && steps[current].next_button && (
          <Button type="primary" onClick={steps[current].next_on_click || (() => message.success('Processing complete!'))}>
            {steps[current].next_button}
          </Button>
        )}
        {current > 0 && steps[current].prev_button && (
          <Button style={{ margin: '0 8px' }} onClick={steps[current].prev_on_click || (() => prev())}>
            {steps[current].prev_button}
          </Button>
        )}
      </div>
    </>
  );
};

export default HeaderSteps;
