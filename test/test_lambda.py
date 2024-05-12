import asyncio
import unittest
import tracemalloc 
from unittest.mock import MagicMock, patch
from utils.get_marvel_characters import fetch_characters, get_all_characters, main, upload_to_s3

class TestMarvelAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tracemalloc.start()  
    @classmethod
    def tearDownClass(cls):
        tracemalloc.stop()  


    @patch('utils.get_marvel_characters.asyncio.gather')
    @patch('utils.get_marvel_characters.fetch_characters')
    async def test_get_all_characters(self, mock_fetch_characters, mock_gather):
        """
            Mock data for the fetch_characters function and the asyncio.gather function
        """

        mock_response = {'data': {'total': 200, 'results': [{'id': 1, 'name': 'Character1', 'comics': {'available': 10}}]}}
        mock_fetch_characters.return_value = mock_response

        mock_gather.return_value = [mock_response] * 2

        characters = await get_all_characters('public_key', 'private_key')

        self.assertEqual(len(characters), 200)  # Total characters should be 200

    @patch('utils.get_marvel_characters.upload_to_s3')
    @patch('utils.get_marvel_characters.wr.s3.read_csv')
    async def test_main(self, mock_read_csv, mock_upload_to_s3):
        """
            Mock data  for existind df and the new df
        """
        mock_existing_df = MagicMock()
        mock_existing_df.empty = False
        mock_read_csv.return_value = mock_existing_df

        mock_new_df = MagicMock()
        mock_new_df.empty = False

        await main('public_key', 'private_key', 'boto_session')

        mock_upload_to_s3.assert_called_once_with(mock_new_df, 'boto_session')

    @patch('utils.get_marvel_characters.upload_to_s3')
    @patch('utils.get_marvel_characters.wr.s3.read_csv')
    async def test_main_no_existing_file(self, mock_read_csv, mock_upload_to_s3):

        # Mock data for existing_df
        mock_read_csv.side_effect = Exception()

        # Mock data for new_df
        mock_new_df = MagicMock()
        mock_new_df.empty = False

        await main('public_key', 'private_key', 'boto_session')

        mock_upload_to_s3.assert_called_once_with(mock_new_df, 'boto_session')

if __name__ == '__main__':
    asyncio.run(unittest.main())
  