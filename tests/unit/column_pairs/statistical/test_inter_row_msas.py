from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from sdmetrics.column_pairs import InterRowMSAS


class TestInterRowMSAS:
    def test_compute_breakdown(self):
        """Test `compute_breakdown` works."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4, 5, 6])
        synthetic_keys = pd.Series(['id3', 'id3', 'id3', 'id4', 'id4', 'id4'])
        synthetic_values = pd.Series([1, 10, 3, 7, 5, 1])

        metric = InterRowMSAS()

        # Run
        result = metric.compute_breakdown(
            real_data=(real_keys, real_values), synthetic_data=(synthetic_keys, synthetic_values)
        )

        # Assert
        assert result == {'score': 0.5}

    def test_compute(self):
        """Test it runs."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4, 5, 6])
        synthetic_keys = pd.Series(['id3', 'id3', 'id3', 'id4', 'id4', 'id4'])
        synthetic_values = pd.Series([1, 10, 3, 7, 5, 1])

        # Run
        score = InterRowMSAS.compute(
            real_data=(real_keys, real_values), synthetic_data=(synthetic_keys, synthetic_values)
        )

        # Assert
        assert score == 0.5

    def test_compute_nans(self):
        """Test it runs with nans."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 2, np.nan, 4, 5, 8])
        synthetic_keys = pd.Series(['id3', 'id3', 'id3', 'id4', 'id4', 'id4'])
        synthetic_values = pd.Series([1, 10, 4, 7, np.nan, np.nan])

        # Run
        score = InterRowMSAS.compute(
            real_data=(real_keys, real_values), synthetic_data=(synthetic_keys, synthetic_values)
        )

        # Assert
        assert score == 0.5

    def test_compute_identical_sequences(self):
        """Test it returns 1 when real and synthetic data are identical."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4, 5, 6])
        synthetic_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        synthetic_values = pd.Series([1, 2, 3, 4, 5, 6])

        # Run
        score = InterRowMSAS.compute(
            real_data=(real_keys, real_values), synthetic_data=(synthetic_keys, synthetic_values)
        )

        # Assert
        assert score == 1

    def test_compute_different_sequences(self):
        """Test it for distinct distributions."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4, 5, 6])
        synthetic_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        synthetic_values = pd.Series([1, 3, 5, 2, 4, 6])

        # Run
        score = InterRowMSAS.compute(
            real_data=(real_keys, real_values), synthetic_data=(synthetic_keys, synthetic_values)
        )

        # Assert
        assert score == 0

    def test_compute_with_log(self):
        """Test it with logarithmic transformation."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 4, 8, 16, 32])
        synthetic_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        synthetic_values = pd.Series([1, 2, 4, 8, 16, 32])

        # Run
        score = InterRowMSAS.compute(
            real_data=(real_keys, real_values),
            synthetic_data=(synthetic_keys, synthetic_values),
            apply_log=True,
        )

        # Assert
        assert score == 1

    def test_compute_with_log_warning(self):
        """Test it warns when negative values are present and apply_log is True."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 1.4, 4, -1, 16, -10])
        synthetic_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        synthetic_values = pd.Series([1, 2, -4, 8, 16, 30])

        # Run
        with pytest.warns(UserWarning) as warning_info:
            score = InterRowMSAS.compute(
                real_data=(real_keys, real_values),
                synthetic_data=(synthetic_keys, synthetic_values),
                apply_log=True,
            )

        # Assert
        expected_message = (
            'There are 3 non-positive values in your data, which cannot be used with log. '
            "Consider changing 'apply_log' to False for a better result."
        )

        assert len(warning_info) == 1
        assert str(warning_info[0].message) == expected_message
        assert score == 0.5

    def test_compute_with_log_datetime(self):
        """Test it crashes for logs of datetime values."""
        # Setup
        real_keys = pd.Series(['id1', 'id1'])
        real_values = pd.Series([datetime(2020, 10, 1), datetime(2020, 10, 1)])
        synthetic_keys = pd.Series(['id2', 'id2'])
        synthetic_values = pd.Series([datetime(2020, 10, 1), datetime(2020, 10, 1)])

        # Run and Assert
        err_msg = (
            'Cannot compute log for datetime columns. '
            "Please set 'apply_log' to False to use this metric."
        )
        with pytest.raises(TypeError, match=err_msg):
            InterRowMSAS.compute(
                real_data=(real_keys, real_values),
                synthetic_data=(synthetic_keys, synthetic_values),
                apply_log=True,
            )

    def test_compute_different_n_rows_diff(self):
        """Test it with different n_rows_diff."""
        # Setup
        real_keys = pd.Series(['id1'] * 10 + ['id2'] * 10)
        real_values = pd.Series(list(range(10)) + list(range(10)))
        synthetic_keys = pd.Series(['id1'] * 10 + ['id2'] * 10)
        synthetic_values = pd.Series(list(range(10)) + list(range(10)))

        # Run
        score = InterRowMSAS.compute(
            real_data=(real_keys, real_values),
            synthetic_data=(synthetic_keys, synthetic_values),
            n_rows_diff=3,
        )

        # Assert
        assert score == 1

    def test_compute_invalid_real_data(self):
        """Test that it raises ValueError when real_data is invalid."""
        # Setup
        real_data = [[1, 2, 3], [4, 5, 6]]  # Not a tuple of pandas Series
        synthetic_keys = pd.Series(['id1', 'id1', 'id2', 'id2'])
        synthetic_values = pd.Series([1, 2, 3, 4])

        # Run and Assert
        with pytest.raises(ValueError, match='The data must be a tuple of two pandas series.'):
            InterRowMSAS.compute(
                real_data=real_data,
                synthetic_data=(synthetic_keys, synthetic_values),
                n_rows_diff=1,
                apply_log=False,
            )

    def test_compute_invalid_synthetic_data(self):
        """Test that it raises ValueError when synthetic_data is invalid."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4])
        synthetic_data = [[1, 2, 3], [4, 5, 6]]  # Not a tuple of pandas Series

        # Run and Assert
        with pytest.raises(ValueError, match='The data must be a tuple of two pandas series.'):
            InterRowMSAS.compute(
                real_data=(real_keys, real_values),
                synthetic_data=synthetic_data,
                n_rows_diff=1,
                apply_log=False,
            )

    def test_compute_invalid_n_rows_diff(self):
        """Test that it raises ValueError when n_rows_diff is invalid."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4])
        synthetic_keys = pd.Series(['id3', 'id3', 'id4', 'id4'])
        synthetic_values = pd.Series([1, 2, 3, 4])

        # Run and Assert
        with pytest.raises(ValueError, match="'n_rows_diff' must be an integer greater than zero."):
            InterRowMSAS.compute(
                real_data=(real_keys, real_values),
                synthetic_data=(synthetic_keys, synthetic_values),
                n_rows_diff=0,
                apply_log=False,
            )

    def test_compute_invalid_apply_log(self):
        """Test that it raises ValueError when apply_log is invalid."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4])
        synthetic_keys = pd.Series(['id1', 'id1', 'id2', 'id2'])
        synthetic_values = pd.Series([1, 2, 3, 4])

        # Run and Assert
        with pytest.raises(ValueError, match="'apply_log' must be a boolean."):
            InterRowMSAS.compute(
                real_data=(real_keys, real_values),
                synthetic_data=(synthetic_keys, synthetic_values),
                n_rows_diff=1,
                apply_log='True',  # Should be a boolean, not a string
            )

    def test_compute_warning(self):
        """Test a warning is raised when n_rows_diff is greater than sequence values size."""
        # Setup
        real_keys = pd.Series(['id1', 'id1', 'id1', 'id2', 'id2', 'id2'])
        real_values = pd.Series([1, 2, 3, 4, 5, 6])
        synthetic_keys = pd.Series(['id3', 'id3', 'id3', 'id4', 'id4', 'id4'])
        synthetic_values = pd.Series([1, 10, 3, 7, 5, 1])

        # Run and Assert
        warn_msg = (
            "n_rows_diff '10' is greater or equal to the size of 2 sequence keys in real_data."
        )
        with pytest.warns(UserWarning, match=warn_msg):
            score = InterRowMSAS.compute(
                real_data=(real_keys, real_values),
                synthetic_data=(synthetic_keys, synthetic_values),
                n_rows_diff=10,
            )

        # Assert
        assert pd.isna(score)
