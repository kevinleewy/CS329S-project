import React, { useState } from 'react';

import { Card, Rate } from 'antd';

const { Meta } = Card;

export default function ProductCard({name, uri, price, rating, link}) {
  console.log(name, price, rating, link);
  return (
    <Card
      hoverable
      style={{ width: 240 }}
      cover={<img alt="name" src={uri} />}
    >
      <Meta title={price} description={""} />
      <Rate disabled value={rating} />
    </Card>
  )
}
