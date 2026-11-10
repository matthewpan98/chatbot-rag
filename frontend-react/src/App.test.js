import { render, screen } from '@testing-library/react';
import App from './App';

// react-markdown è un modulo ESM che Jest (create-react-app) non sa leggere: nei test lo sostituiamo
jest.mock('react-markdown', () => (props) => <div>{props.children}</div>);

test('mostra la chat con il messaggio di benvenuto', () => {
  render(<App />);
  expect(screen.getByText(/ASSISTENTE VIRTUALE LLM/i)).toBeInTheDocument();
  expect(screen.getByText(/Come posso aiutarti/i)).toBeInTheDocument();
});
