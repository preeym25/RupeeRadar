"""Transaction parser service for different file formats."""

import pandas as pd
import pdfplumber
from datetime import datetime
from typing import List, Dict
import chardet


class TransactionParser:
    """Parse different bank statement formats (CSV, Excel, PDF)."""
    
    @staticmethod
    def parse_csv(file_path: str) -> List[Dict]:
        """Parse CSV bank statement."""
        try:
            df = pd.read_csv(file_path)
            transactions = []
            
            for idx, row in df.iterrows():
                # Try to extract date
                date_str = None
                for col in ['Date', 'date', 'Transaction Date', 'transaction_date']:
                    if col in df.columns:
                        date_str = row.get(col)
                        break
                
                # Try to extract amount
                amount = None
                for col in ['Amount', 'amount', 'Debit', 'Credit']:
                    if col in df.columns:
                        try:
                            amount = float(row.get(col, 0))
                            break
                        except:
                            pass
                
                # Try to extract description
                description = None
                for col in ['Description', 'description', 'Remarks', 'remarks', 'Particulars']:
                    if col in df.columns:
                        description = str(row.get(col, ''))
                        break
                
                if date_str and amount and description:
                    transaction = {
                        'date': pd.to_datetime(date_str, errors='coerce'),
                        'amount': abs(float(amount)),
                        'description': description,
                        'type': 'DEBIT' if float(amount) < 0 else 'CREDIT',
                        'raw_data': row.to_dict(),
                        'source_row': idx + 2  # +2 for 1-based indexing and header
                    }
                    if pd.notna(transaction['date']):
                        transactions.append(transaction)
            
            return transactions
        
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")
    
    @staticmethod
    def parse_excel(file_path: str) -> List[Dict]:
        """Parse Excel bank statement."""
        try:
            df = pd.read_excel(file_path)
            # Similar logic to CSV parsing
            transactions = []
            
            for idx, row in df.iterrows():
                # Extract date
                date_str = None
                for col in ['Date', 'date', 'Transaction Date', 'transaction_date']:
                    if col in df.columns:
                        date_str = row.get(col)
                        break
                
                # Extract amount
                amount = None
                for col in ['Amount', 'amount', 'Debit', 'Credit']:
                    if col in df.columns:
                        try:
                            amount = float(row.get(col, 0))
                            break
                        except:
                            pass
                
                # Extract description
                description = None
                for col in ['Description', 'description', 'Remarks', 'remarks', 'Particulars']:
                    if col in df.columns:
                        description = str(row.get(col, ''))
                        break
                
                if date_str and amount and description:
                    transaction = {
                        'date': pd.to_datetime(date_str, errors='coerce'),
                        'amount': abs(float(amount)),
                        'description': description,
                        'type': 'DEBIT' if float(amount) < 0 else 'CREDIT',
                        'raw_data': row.to_dict(),
                        'source_row': idx + 2
                    }
                    if pd.notna(transaction['date']):
                        transactions.append(transaction)
            
            return transactions
        
        except Exception as e:
            raise ValueError(f"Error parsing Excel: {str(e)}")
    
    @staticmethod
    def parse_pdf(file_path: str) -> List[Dict]:
        """Parse PDF bank statement."""
        try:
            transactions = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    
                    if tables:
                        for table in tables:
                            for row in table[1:]:  # Skip header
                                if row and len(row) >= 3:
                                    try:
                                        date_str = row[0]
                                        amount = float(row[1])
                                        description = row[2] if len(row) > 2 else "PDF Transaction"
                                        
                                        transaction = {
                                            'date': pd.to_datetime(date_str, errors='coerce'),
                                            'amount': abs(amount),
                                            'description': description,
                                            'type': 'DEBIT' if amount < 0 else 'CREDIT',
                                            'raw_data': {'page': page_num, 'row': row},
                                            'source_row': page_num
                                        }
                                        if pd.notna(transaction['date']):
                                            transactions.append(transaction)
                                    except:
                                        pass
            
            return transactions
        
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Detect file encoding."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'
    
    @staticmethod
    def auto_detect_format(file_path: str, file_type: str) -> List[Dict]:
        """Auto-detect and parse any supported format."""
        file_type = file_type.lower()
        
        if file_type in ['csv', 'txt']:
            return TransactionParser.parse_csv(file_path)
        elif file_type in ['xlsx', 'xls']:
            return TransactionParser.parse_excel(file_path)
        elif file_type == 'pdf':
            return TransactionParser.parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
