import React, { createRef, useRef, useState, useEffect } from 'react';
import axios from "axios";

import {
  Carousel,
  Divider,
  Layout,
  Menu,
  Breadcrumb,
  Button,
  Row,
  Col,
  Dropdown,
  Space,
  Tooltip,
  Slider,
  Radio,
  Form,
  InputNumber,
  Checkbox,
  Rate,
  message,
} from 'antd';
import Icon, {FileImageOutlined, DownOutlined, SlidersOutlined, HomeOutlined, SkinOutlined, UploadOutlined, FireOutlined, LoadingOutlined, UserOutlined, PlusOutlined} from '@ant-design/icons';
import styled from "styled-components";

import "antd/dist/antd.css"
// import './styles.css';

import HeaderSteps from '../../components/Steps/Steps';
import SwipableCards from '../../components/SwipableCards/SwipableCards';
import UploadSection from '../../components/UploadSection/UploadSection';
import ProductCard from '../../components/ProductCard/ProductCard';
import { GET_RECOMMENDATIONS } from '../../apiPaths';


const { SubMenu } = Menu;
const { Header, Content, Footer, Sider } = Layout;

const Title = styled.div`
  font-size: 24px;
  color: black;
  text-align: left;
`;

const StyledSwipableCards = styled(SwipableCards)`
  background: red; // #f9fafb;
  // width: 300px;
  // height: 400px;
  // display: flex;
  // align-items: center;
  // justify-content: center;
  // flex-direction: column;
  // font-size: 150px;
  text-shadow: 0 10px 10px #d1d5db;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  border-radius: 50px;
  border: red;
  background-color: red !important;
`


function beforeUpload(file) {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('You can only upload JPG/PNG file!');
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('Image must smaller than 2MB!');
  }
  return isJpgOrPng && isLt2M;
}


function handleButtonClick(e) {
  message.info('Click on left button.');
  console.log('click left button', e);
}


function handleMenuClick(e) {
  // message.info('Click on menu item.');
  // console.log('click', e);
}


function DecimalStep({min, max, lowValue, setLowValue, highValue, setHighValue}) {
  const onLowChange = (value) => {
    if (isNaN(value)) {
      return;
    }
    setLowValue(value);
  };

  const onHighChange = (value) => {
    if (isNaN(value)) {
      return;
    }
    setHighValue(value);
  };

  const onChange = (value) => {
    if (isNaN(value[0]) || isNaN(value[1])) {
      return;
    }
    setLowValue(value[0]);
    setHighValue(value[1]);
  }

  return (
    <Row gutter={8}>
      <Col span={4}>
        <InputNumber
          min={min}
          max={highValue}
          formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
          parser={value => value.replace(/\$\s?|(,*)/g, '')}
          style={{ margin: '0 0' }}
          step={1}
          value={lowValue}
          onChange={onLowChange}
        />
      </Col>
      <Col span={16}>
        <Slider
          min={min}
          max={max}
          range={{ draggableTrack: true }}
          onChange={onChange}
          value={[lowValue, highValue]}
          defaultValue={[min, max]}
          step={1}
        />
      </Col>
      <Col span={4}>
        <InputNumber
          min={lowValue}
          max={max}
          formatter={value => `$ ${value}`.replace(/\B(?=(\d{4})+(?!\d))/g, ',')}
          parser={value => value.replace(/\$\s?|(,*)/g, '')}
          style={{ margin: '0 0' }}
          step={1}
          value={highValue}
          onChange={onHighChange}
        />
      </Col>
    </Row>
  );
}


function FilterMenu(min, max, onSubmit) {
  const [lowValue, setLowValue] = useState(min);
  const [highValue, setHighValue] = useState(max);
  // const [rating, setRating] = useState(0);

  const onFinish = (results) => {
    const final_results = {
      ...results,
      minPrice: lowValue,
      maxPrice: highValue,
    };
    onSubmit(final_results);
  };

  return (
    <Form style={{width: "630px", padding: "16px"}} onFinish={onFinish}>
      <div style={{fontSize: "18px", fontWeight: "bold"}}>Filter Outfits</div>
      <Divider style={{margin: "8px 0 16px"}} />
      <Row>
        <Col span={12}>
          <Form.Item name="type">
            <Checkbox.Group>
              <Checkbox value="mens" style={{ lineHeight: '32px' }}>
                Men's
              </Checkbox>
              <Checkbox value="womens" style={{ lineHeight: '32px' }}>
                Women's
              </Checkbox>
            </Checkbox.Group>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="rating" label="Minimum Rating:">
            <Rate allowHalf />
          </Form.Item>
        </Col>
      </Row>
      <div key="price">
        <div>Price</div>
        <DecimalStep min={min} max={max} lowValue={lowValue} setLowValue={setLowValue} highValue={highValue} setHighValue={setHighValue} />
      </div>
      <Divider style={{margin: "24px 0 12px"}} />
      <Form.Item  style={{margin: 0}}>
        <Button type="primary" htmlType="submit" style={{margin: 0}}>
          Filter
        </Button>
      </Form.Item>
    </Form>
  );
};


function SearchPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [imageUrl, setImageUrl] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [visible, setVisible] = useState(false);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    axios.post(GET_RECOMMENDATIONS)
    .then(function (response) {
      console.log(response);
      setSearchResults([...response.data]);
      return response.data
    })
    .catch(function (error) {
      console.log(error);
    });
  }, []);

  const onSubmit = (filters) => {
    console.log(filters)
  };

  const matchesFilters = (item) => {
    return (
      (filters.rating && item.rating && item.rating >= filters.rating) &&
      (filters.minPrice && item.rating && item.price >= filters.minPrice) &&
      (filters.maxPrice && item.rating && item.price <= filters.maxPrice)
    )
  }

  return (
    <>
      <Row>
        <Col span={22}>
          <Breadcrumb style={{ margin: '16px 0 0', textAlign: 'left' }}>
            <Breadcrumb.Item>
              <HomeOutlined />
            </Breadcrumb.Item>
            <Breadcrumb.Item>
              Search
            </Breadcrumb.Item>
          </Breadcrumb>
          <Title style={{marginBottom: "12px"}}>Search for Outfits</Title>
        </Col>
        <Col span={2}>
          <Dropdown.Button
            style={{ margin: '32px 0 0', fontSize: "25px"}}
            onClick={handleButtonClick}
            overlay={FilterMenu(0, 100, onSubmit)}
            trigger={["click"]}
            icon={<SlidersOutlined />}
            visible={visible}
            onVisibleChange={setVisible}
          >
            Filter
          </Dropdown.Button>
        </Col>
      </Row>
      
      <div key={"slide3-${searchResults.length}imgs"} className="steps-content">
        <br />
        <Row gutter={[16, 16]}>
          {searchResults.map(item => {matchesFilters(item) && (
            <Col span={4}>
              <ProductCard {...item} />
            </Col>
          )})}
        </Row>
        {searchResults.length === 0 && (
          <>
            <br />
            <br />
            <br />
            <img src="https://alahausse.ca/wp-content/uploads/2021/08/giphy-phone.gif" />
          </>
        )}
        <br />
      </div>
    </>
  )
}

export default SearchPage;
