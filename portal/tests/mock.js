function Mock(description, mocks) {
	this.description = description || '';
	this.mocks = mocks || [];
	this.mockString = this.mocks.join(',');
}

module.exports = Mock;