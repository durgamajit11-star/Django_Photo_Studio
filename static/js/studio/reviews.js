(function () {
    const chartNode = document.getElementById('ratingDistributionChart');
    const ratingDataNode = document.getElementById('studioRatingDistributionData');

    function getThemeColors() {
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        return {
            axis: isLight ? '#60728b' : '#9eb0cb',
            grid: isLight ? 'rgba(21,34,56,0.08)' : 'rgba(255,255,255,0.05)',
        };
    }

    function buildChart() {
        if (!chartNode || !ratingDataNode || typeof Chart === 'undefined') {
            return;
        }

        const ratingDistribution = JSON.parse(ratingDataNode.textContent || '[]');
        const colors = getThemeColors();

        new Chart(chartNode.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['5★', '4★', '3★', '2★', '1★'],
                datasets: [{
                    data: ratingDistribution.length ? ratingDistribution : [0, 0, 0, 0, 0],
                    backgroundColor: ['#10b981', '#06b6d4', '#f59e0b', '#ef4444', '#94a3b8'],
                    borderRadius: 6,
                    maxBarThickness: 24,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.raw + ' review(s)';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: colors.grid },
                        ticks: {
                            color: colors.axis,
                            precision: 0,
                            callback: function (value) {
                                return Number(value).toFixed(0);
                            }
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: colors.axis }
                    }
                }
            }
        });
    }

    const ratingFilter = document.getElementById('ratingFilter');
    const sortFilter = document.getElementById('sortFilter');
    const reviewSearch = document.getElementById('reviewSearch');
    const reviewsList = document.getElementById('reviewsList');
    const visibleCountNode = document.getElementById('visibleReviewCount');
    const emptyAfterFilterNode = document.getElementById('reviewFilterEmptyState');
    const exportBtn = document.getElementById('exportReviewsBtn');

    function getCards() {
        return Array.from(document.querySelectorAll('.review-card'));
    }

    function sortCards(cards) {
        if (!reviewsList || !sortFilter) {
            return;
        }

        const sortValue = sortFilter.value;
        cards.sort(function (a, b) {
            const aRating = Number(a.dataset.rating || 0);
            const bRating = Number(b.dataset.rating || 0);
            const aTime = Number(a.dataset.timestamp || 0);
            const bTime = Number(b.dataset.timestamp || 0);

            if (sortValue === 'oldest') {
                return aTime - bTime;
            }

            if (sortValue === 'high') {
                return bRating - aRating || bTime - aTime;
            }

            if (sortValue === 'low') {
                return aRating - bRating || bTime - aTime;
            }

            return bTime - aTime;
        });

        cards.forEach(function (card) {
            reviewsList.appendChild(card);
        });
    }

    function applyFilters() {
        const cards = getCards();
        const selectedRating = ratingFilter ? ratingFilter.value : '';
        const term = reviewSearch ? reviewSearch.value.trim().toLowerCase() : '';

        let visible = 0;
        cards.forEach(function (card) {
            const cardRating = card.dataset.rating || '';
            const content = (card.textContent || '').toLowerCase();
            const matchesRating = !selectedRating || cardRating === selectedRating;
            const matchesSearch = !term || content.includes(term);
            const show = matchesRating && matchesSearch;
            card.style.display = show ? '' : 'none';
            if (show) {
                visible += 1;
            }
        });

        if (visibleCountNode) {
            visibleCountNode.textContent = 'Showing ' + visible + ' review' + (visible === 1 ? '' : 's');
        }

        if (emptyAfterFilterNode) {
            emptyAfterFilterNode.classList.toggle('d-none', visible !== 0 || cards.length === 0);
        }
    }

    function exportVisibleReviews() {
        const visibleCards = getCards().filter(function (card) {
            return card.style.display !== 'none';
        });

        if (!visibleCards.length) {
            alert('No visible reviews to export.');
            return;
        }

        const rows = [['Reviewer', 'Email', 'Rating', 'Date', 'Comment']];
        visibleCards.forEach(function (card) {
            const reviewer = card.querySelector('.reviewer-info strong')?.textContent?.trim() || '';
            const email = card.querySelector('.reviewer-info small')?.textContent?.trim() || '';
            const ratingText = card.querySelector('.rating-badge')?.textContent?.trim() || '';
            const dateText = card.querySelector('.review-footer small')?.textContent?.replace(/\s+/g, ' ').trim() || '';
            const comment = card.querySelector('.review-body p')?.textContent?.replace(/\s+/g, ' ').trim() || '';
            rows.push([reviewer, email, ratingText, dateText, comment]);
        });

        const csv = rows
            .map(function (row) {
                return row
                    .map(function (value) {
                        const safe = String(value || '').replace(/"/g, '""');
                        return '"' + safe + '"';
                    })
                    .join(',');
            })
            .join('\n');

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'studio-reviews.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    document.querySelectorAll('.review-progress-bar').forEach(function (node) {
        const value = Number(node.dataset.width || 0);
        node.style.width = Math.min(100, Math.max(0, value)) + '%';
    });

    if (sortFilter) {
        sortFilter.addEventListener('change', function () {
            sortCards(getCards());
            applyFilters();
        });
    }

    if (ratingFilter) {
        ratingFilter.addEventListener('change', applyFilters);
    }

    if (reviewSearch) {
        reviewSearch.addEventListener('input', applyFilters);
    }

    if (exportBtn) {
        exportBtn.addEventListener('click', exportVisibleReviews);
    }

    buildChart();
    sortCards(getCards());
    applyFilters();
})();
