import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders application name', () => {
  render(<App />);
  const applicatioName = screen.getByText(/Algorand Counter App/i);
  expect(applicatioName).toBeInTheDocument();
});
